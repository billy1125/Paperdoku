# 搜尋策略與涵蓋盤點（scoping-strategy）

發現期盤點的可信度取決於搜尋的**透明與完整**。所有搜尋一律透過 `paper-search`／MCP（`semantic-scholar`、`openalex`）取得，禁止憑記憶捏造文獻。

## 一、把問題拆成可搜尋概念

1. 用 PICO／PECO 或「主題＋方法＋對象」抓 2–4 個核心概念。
2. 每個概念列同義詞、縮寫、上下位詞、相關術語（如 "generative AI" ≈ "large language models" ≈ "ChatGPT"）。
3. 規劃布林組合：概念內用 OR，概念間用 AND；必要時用 NOT 排除明顯雜訊。
4. 學術搜尋用**英文名詞片語**命中率最高（"transformer attention mechanism" 優於整句）。

## 二、MCP 取向的搜尋動作

**Semantic Scholar**：`search_papers`／`paper_relevance_search`（帶 year、fields_of_study、min_citation_count）、`get_paper`（單篇完整）、`get_paper_citations`／`get_paper_references`（追引用）。

**OpenAlex**：`search_works`／`search_by_topic`（主題探索）、`find_review_articles`（找回顧文章，快速掌握版圖）、`find_seminal_papers`（奠基之作）、`get_top_cited_works`（高被引）、`get_related_works`、`get_citation_network`、`check_venue_quality`／`list_journal_presets`（UTD24／FT50／AJG 等期刊分級）、`autocomplete_search`（補全查詢詞）。

兩源涵蓋互補，可擇一或併用；一源查無改用另一源再查。

## 三、涵蓋盤點與 PRISMA-lite 計數

盤點不必窮盡，但要能重現。記錄並在產物中呈現：

- **每次搜尋**：資料源、查詢字串、年份範圍、篩選、日期、命中數。
- **計數流程**：初始命中 → 去重後（優先 DOI，其次正規化題名）→ 題名/摘要篩選後 → 納入盤點；每步記排除數與主要排除理由。
- 這是輕量計數，**不是**後段的完整 PRISMA（全文逐篇篩選＋逐篇 RoB）；要完整 PRISMA 導去 `literature-review-organizer`。

## 四、引用鏈追蹤（補足版圖）

- **前向**（誰引用了關鍵文獻）：`get_paper_citations`／`get_work_citations`——找出建立在奠基之作上的新研究。
- **後向**（關鍵文獻引用了誰）：`get_paper_references`／`get_work_references`——找反覆被多篇納入文獻共同引用的基礎文獻。
- 用 `find_review_articles` 先抓近期回顧，能快速定位版圖與既有缺口討論。

## 五、期刊與品質訊號（次要，不當效度）

引用數、期刊分級、作者聲望只是**次要排序訊號**，有年代與領域偏誤，不能當研究效度的證據。跨篇衡量證據強弱用 `../_shared/evidence_hierarchy.md`（meta > RCT > cohort … 的等級）。preprint 明確標示、可信度待同儕審查。

## 六、盤點常見陷阱

- **單一資料源**：漏文獻；至少考慮兩源互補。
- **搜尋無紀錄**：無法重現、缺口宣稱失去可信度；一律記策略。
- **太廣**：上千筆雜訊；用更精確詞組收斂。
- **太窄**：漏相關；補同義詞與相關詞。
- **把「沒查到」當「沒人做」**：反缺口膨脹，見 `gap-taxonomy.md` 與共用紀律。
- **直接複製 abstract**：摘要一律改寫。
- **引用數當即時真值**：註明為查詢當下數字。
