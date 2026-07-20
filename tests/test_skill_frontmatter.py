#!/usr/bin/env python3
"""Guard: every SKILL.md must have a parseable YAML frontmatter.

A full-width colon (U+FF1A `：`) in a frontmatter key (e.g. `description：`)
silently breaks YAML parsing, so Claude Code cannot load the skill. This test
parses each `.claude/skills/*/SKILL.md` frontmatter with yaml.safe_load and
asserts the required keys are present.

Run:
    conda run -n research python tests/test_skill_frontmatter.py

Exit 0 and 'ALL PASS' when every frontmatter parses; 1 otherwise.
"""
import glob
import io
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, ".claude", "skills")
REQUIRED = ("name", "description", "version")


def log(msg):
    sys.stdout.write(msg.encode("ascii", "replace").decode("ascii") + "\n")


def frontmatter(text):
    """Return the YAML block between the leading '---' fences, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    body = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "\n".join(body)
        body.append(line)
    return None


def main():
    files = sorted(glob.glob(os.path.join(SKILLS, "*", "SKILL.md")))
    if not files:
        log("[FAIL] no SKILL.md found under %s" % SKILLS)
        return 1

    failures = []
    for f in files:
        name = os.path.basename(os.path.dirname(f))
        with io.open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
        fm = frontmatter(text)
        if fm is None:
            failures.append((name, "no frontmatter block (missing --- fences)"))
            continue
        try:
            data = yaml.safe_load(fm)
        except yaml.YAMLError as e:
            # Most common cause: a full-width colon in a key.
            detail = str(e).replace("\n", " ")
            hint = " (full-width colon in a key?)" if "：" in fm else ""
            failures.append((name, "YAML parse error: %s%s" % (detail[:160], hint)))
            continue
        if not isinstance(data, dict):
            failures.append((name, "frontmatter is not a mapping"))
            continue
        missing = [k for k in REQUIRED if k not in data]
        if missing:
            failures.append((name, "missing keys: %s" % ", ".join(missing)))
            continue
        log("[PASS] %s  (%s)" % (name, ", ".join("%s" % k for k in REQUIRED)))

    log("-" * 60)
    if failures:
        for name, why in failures:
            log("[FAIL] %s  %s" % (name, why))
        log("SOME CHECKS FAILED")
        return 1
    log("ALL PASS (%d SKILL.md)" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
