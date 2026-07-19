---
name: citation-verification-zh
description： 逐條查核一篇論文（或一份參考文獻清單）中的引用是否真的存在，透過 Semantic Scholar 比對，揪出可能的幻覺引用或引錯的文獻，並標記污染風險訊號。輸出每條引用的查核結果表（找到／查無／資訊不足）＋摘要。當使用者要求「查一下這篇的參考文獻是不是真的」「這些引用存在嗎」「幫我驗證 bibliography」「有沒有幻覺引用」「reference check／citation check」，或在審稿／讀 AI 生成文稿時想確認引用真偽時使用。注意：查無不等於一定是假的（可能只是未被索引，如書籍、非英文、極新文獻）——本 skill 給的是 advisory 風險訊號，不是最終判定。路由：要查「某個宣稱是否有原文證據支持」是另一件事，改用 paper-reading-zh 的 claim-audit 模式；要完整審稿改用 academic-peer-review-zh（可把本 skill 當其中一步）。
version: 0.1.0
---

# 引用存在性驗證（繁體中文）

給定一篇論文或一份參考文獻清單，**逐條查核每個引用是否真的存在**，揪出可能的幻覺引用（尤其 AI 生成文稿常見）或明顯引錯的文獻。

> **最高原則（Anti-leakage）**：見 `../_shared/anti_leakage.md`。**絕不可憑模型記憶「確認」一條引用存在**——每一條都必須實際透過 Semantic Scholar 查詢；查不到就是查不到，不用記憶腦補一個 DOI 或「我記得有這篇」。這正是本 skill 存在的理由：模型記憶會產生看似真實的假引用。
>
> 輸出語言見 `../_shared/output_language.md`；資訊不足時的語氣見 `../_shared/confidence_language.md`。

## 前置需求（Semantic Scholar MCP）

本 skill 依賴 `semantic-scholar` MCP server（與 `paper-search` skill 共用，設定見 `paper-search/.mcp.json`）。

- 查核前先確認 MCP 可用：在 Claude Code 輸入 `/mcp`，確認 `semantic-scholar` 為 connected。
- **MCP 不可用時，不要憑記憶判定引用真偽**——明確告知使用者 MCP 未連線、無法查核，並引導其依 `paper-search/README.md` 排查（`uvx` 安裝、API key）。這是 graceful degradation，不是改用記憶。

## 工作流程

1. **取得參考文獻清單**：
   - 使用者直接貼上引用清單 → 直接用。
   - 給的是整篇論文（PDF）→ 先用 `source-document-extraction` 抽全文，再擷取其 References／參考文獻段落。
   - 只給正文有 in-text citation 但無完整清單 → 提醒使用者：能查的是「參考文獻條目」，in-text 對應需有完整書目資訊才可查。

2. **逐條查核**（每條引用）：
   - 用 `search_papers` / `paper_relevance_search` 以**標題**為主查詢，輔以第一作者姓氏與年份縮小範圍。
   - 命中候選後，用 `get_paper` 取回完整 metadata（標題、作者、年份、DOI），與引用逐欄比對。

3. **分類判定**（四態，見 `references/verdict-rules.md`）：
   | 判定 | 意義 |
   |---|---|
   | ✅ 找到 | Semantic Scholar 有對應條目，標題／作者／年份相符 |
   | ⚠️ 查無 | 查不到相符條目——**可能是幻覺，也可能只是未被索引**（書籍、非英文、極新、灰色文獻） |
   | 🔶 資訊不足 | 引用書目殘缺（無標題或關鍵欄位），無法查 |
   | ⛔ 無法查核 | MCP 不可用（降級，非引用本身問題） |

4. **相稱檢查**（命中時）：命中條目的標題／作者與引用明顯不符 → 標記「可能引錯文獻」（找到了另一篇，不是宣稱的那篇）。

5. **污染風險 advisory**（借 ARS 污染訊號，僅提示不判定）：對「查無」的條目，若同時是**預印本且年份較新（2024 後）**，標為較高風險；細節見 `references/verdict-rules.md`。

6. **輸出**：逐條查核表 ＋ 摘要，見下。

## 輸出格式

```markdown
## 引用查核結果

| # | 引用（縮寫） | 判定 | DOI／來源 | 備註 |
|---|---|---|---|---|
| 1 | Chen 2023, "…" | ✅ 找到 | 10.xxxx | — |
| 2 | Wang 2025, "…" | ⚠️ 查無 | — | 預印本＋新，風險較高 |
| 3 | （無標題） | 🔶 資訊不足 | — | 缺標題，無法查 |

## 摘要
- 共查核 N 條：找到 X、查無 Y、資訊不足 Z（、無法查核 W）。
- 需關注：第 2、5 條查無且屬高風險，建議回原文與原始出處人工覆核。
```

## 紀律（務必遵守）

- **查無 ≠ 一定是假的**：一律附上這句 caveat。Semantic Scholar 未收錄書籍、部分非英文與極新文獻；「查無」是**需人工覆核的風險訊號**，不是「這條是編造的」的定論。這是刻意的精確度優先（precision over recall）。
- **不憑記憶補全**：查不到就標查無，不要用記憶「想起」一個 DOI 或作者。
- **可回溯**：每條命中附 DOI／來源連結，讓使用者能自己覆核。
- **當審稿的一步**：`academic-peer-review-zh` 可在方法/文獻面向呼叫本 skill 的結果；但本 skill 只查「引用是否存在」，不評「引用是否支持該宣稱」（後者是 `paper-reading-zh` 的 `claim-audit`）。

## 上下游交接

- **產物**：查核結果表與摘要寫成 markdown 存到 `reports/`（檔名沿用來源主幹＋`citation-check`，見 `../_shared/paper_naming_convention.md`）。
- **上游**：整篇論文的 PDF 先經 `source-document-extraction` 抽成 `extracted/*.md`，再擷取其參考文獻段落；或使用者直接貼參考清單。
- **搭配**：常作為 `academic-peer-review-zh` 或 `literature-review-organizer`(systematic review)的一步。鏈見 `../_shared/handoff.md`。
