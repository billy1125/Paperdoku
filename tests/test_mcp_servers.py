#!/usr/bin/env python3
"""Connectivity test for the paper-search MCP servers (semantic-scholar, openalex).

For each server configured in the project-root `.mcp.json`, this launches
the server exactly as configured, performs a JSON-RPC handshake over stdio, then
asserts three things:

  1. initialize        -> returns serverInfo (server is alive and speaks MCP)
  2. tools/list        -> contains the expected search tool
  3. tools/call search -> returns a non-error result with content (a live query works)

Run:
    conda run -n research python tests/test_mcp_servers.py

Exit code 0 and a final "ALL PASS" line when every check passes; 1 otherwise.
The script depends only on the Python standard library.

Secrets: `${VAR:-default}` placeholders in .mcp.json are expanded from the `env`
block of `.claude/settings.local.json` (gitignored). Credentials are passed into
the child process environment only and are never printed.
"""
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_JSON = ROOT / ".mcp.json"
SETTINGS = ROOT / ".claude" / "settings.local.json"

# Per-server checks. Tool names verified against each server's live tools/list.
SERVER_CHECKS = {
    "semantic-scholar": {"tool": "search_papers", "query": "machine learning"},
    "openalex": {"tool": "search_works", "query": "machine learning"},
}

VAR_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(:-([^}]*))?\}")
PLACEHOLDER = {"YOUR_KEY", "your.email@example.com", ""}


def log(msg):
    # ASCII-safe to avoid cp950 console errors on Windows.
    sys.stdout.write(msg.encode("ascii", "replace").decode("ascii") + "\n")
    sys.stdout.flush()


def load_overrides():
    if not SETTINGS.exists():
        return {}
    return json.loads(SETTINGS.read_text(encoding="utf-8")).get("env", {}) or {}


def expand(value, overrides):
    def repl(m):
        name, _, default = m.group(1), m.group(2), m.group(3) or ""
        return overrides.get(name, os.environ.get(name, default))
    return VAR_RE.sub(repl, value)


def build_child_env(server_env, overrides):
    child = os.environ.copy()
    for key, raw in (server_env or {}).items():
        child[key] = expand(str(raw), overrides)
    return child


def spawn(command, args, env):
    exe = shutil.which(command) or command
    cmd = [exe, *args]
    # On Windows, npm shims are .cmd wrappers that CreateProcess cannot run directly.
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        cmd = ["cmd", "/c", exe, *args]
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )


def _reader(pipe, q):
    for line in pipe:
        q.put(line)
    q.put(None)


def probe(name, command, args, child_env, tool, query, timeout=180):
    """Return (ok, [check_line, ...], diagnostic)."""
    lines = []
    proc = spawn(command, args, child_env)
    q = queue.Queue()
    threading.Thread(target=_reader, args=(proc.stdout, q), daemon=True).start()
    err_lines = []
    threading.Thread(
        target=lambda: err_lines.extend(proc.stderr), daemon=True
    ).start()

    responses = {}

    def send(obj):
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def collect(want, deadline):
        while want - set(responses) and time.time() < deadline:
            try:
                line = q.get(timeout=max(0.1, deadline - time.time()))
            except queue.Empty:
                break
            if line is None:  # stdout EOF
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and msg.get("id") in want:
                responses[msg["id"]] = msg

    ok = True
    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "paperdoku-test", "version": "0.1.0"}}})
        collect({1}, time.time() + timeout)
        init = responses.get(1, {}).get("result")
        server_name = (init or {}).get("serverInfo", {}).get("name")
        if server_name:
            lines.append("[PASS] %s: initialize -> serverInfo '%s'" % (name, server_name))
        else:
            ok = False
            lines.append("[FAIL] %s: no initialize/serverInfo response" % name)
            return ok, lines, "".join(err_lines[-20:])

        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
              "params": {"name": tool, "arguments": {"query": query}}})
        collect({2, 3}, time.time() + timeout)

        tools = (responses.get(2, {}).get("result") or {}).get("tools", [])
        tool_names = {t.get("name") for t in tools}
        if tool in tool_names:
            lines.append("[PASS] %s: tools/list has '%s' (%d tools total)"
                         % (name, tool, len(tool_names)))
        else:
            ok = False
            lines.append("[FAIL] %s: tools/list missing '%s'" % (name, tool))

        call = responses.get(3, {}).get("result")
        err = responses.get(3, {}).get("error")
        if call and not call.get("isError") and (call.get("content") or call.get("structuredContent")):
            lines.append("[PASS] %s: tools/call %s('%s') returned a result"
                         % (name, tool, query))
        else:
            ok = False
            detail = (err or call or "no response")
            lines.append("[FAIL] %s: tools/call %s failed (%s)"
                         % (name, tool, json.dumps(detail)[:200]))
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    return ok, lines, "".join(err_lines[-20:])


def main():
    if not MCP_JSON.exists():
        log("[FAIL] .mcp.json not found at %s" % MCP_JSON)
        return 1
    servers = json.loads(MCP_JSON.read_text(encoding="utf-8")).get("mcpServers", {})
    overrides = load_overrides()

    log("Paperdoku MCP connectivity test")
    log("config: %s" % MCP_JSON)
    log("-" * 60)

    all_ok = True
    for name, checks in SERVER_CHECKS.items():
        cfg = servers.get(name)
        if not cfg:
            all_ok = False
            log("[FAIL] %s: not found in .mcp.json" % name)
            continue
        # Note which optional credentials are active (booleans only, never values).
        active = [k for k, v in (cfg.get("env") or {}).items()
                  if expand(str(v), overrides) not in PLACEHOLDER]
        log("== %s == (credentials set: %s)" % (name, ", ".join(active) or "none"))
        child_env = build_child_env(cfg.get("env"), overrides)
        ok, lines, err = probe(name, cfg["command"], cfg.get("args", []),
                               child_env, checks["tool"], checks["query"])
        for ln in lines:
            log(ln)
        if not ok and err.strip():
            log("  stderr(tail): %s" % err.strip().replace("\n", " | ")[:400])
        all_ok = all_ok and ok
        log("-" * 60)

    if all_ok:
        log("ALL PASS")
        return 0
    log("SOME CHECKS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
