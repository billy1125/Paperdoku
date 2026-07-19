# 圖表查核協定（Figure/Table Fidelity，共用）

> Paperdoku suite 共用規範。查核一張**圖/表是否真的支撐它的 caption 與內文宣稱**。由 `academic-peer-review-zh`（面向 5/8）與 `paper-reading-zh` 的 `claim-audit` 共用。以 `../_shared/figure_fidelity.md` 引用。

## 前置：先把圖變成可看的圖檔

模型要能**看到圖**才能查。圖不在脈絡中時：

1. 用 `source-document-extraction` 的 `--figures` 把含圖的頁 render 成 PNG:
   `conda run -n research python scripts/extract_pdf.py paper.pdf --figures --pages 5-6`
   → 產出 `extracted/figures/paper-p5.png` 等。
2. 用 Read 工具直接讀該 PNG（Claude 本身是多模態，可看圖；不需外接 VLM API）。
3. 同時取 caption 與內文對該圖的宣稱（來自 extracted 的 `.md`）。

> 遵守 `../_shared/anti_leakage.md`：**只根據圖上實際可見的內容判斷**，不憑記憶腦補圖裡有什麼；讀不清就說讀不清，不猜。

## 查核什麼

對每張圖/表：

1. **caption 詮釋是否從圖推得**：caption 宣稱的趨勢/差異/結論，在圖上看得到嗎？
2. **內文宣稱是否被圖支持**：內文引「如 Fig X 所示」支持某主張——圖真的支持該主張、且範圍相稱嗎？
3. **要素相符**：座標軸標籤/單位、N、誤差線、圖例、資料點是否與宣稱一致？

## 常見不相稱型態（可點名）

- **截斷/放大軸**：y 軸不從 0 起或範圍刻意窄，把微小差異畫得很大。
- **無誤差線/區間卻宣稱顯著差異**。
- **相關圖當因果**：散點/趨勢圖被解讀成因果。
- **雙 y 軸誤導**：兩序列用不同軸營造相關假象。
- **3D/面積扭曲比例**：視覺誇大或縮小差距。
- **cherry-picking**：只畫支持宣稱的子集。
- **caption 過度延伸**：圖只顯示 A,caption 卻宣稱 A 導致 B。

## 輸出(advisory)

逐圖給判定，**僅提示供人覆核，不判定造假**：

| 判定 | 意義 |
|---|---|
| 相稱 | 圖/caption/宣稱一致 |
| 部分相稱 | 大致支持但有誇大/範圍不符（如截斷軸） |
| 不相稱 | 圖不支持或與宣稱相反 |
| 讀不清 | 圖太糊/小字/多子圖無法判讀（標明，不硬判） |

每張附一句理由（對應上面查什麼/不相稱型態）。

## 紀律（誠實面對 VLM 極限）

- **能判趨勢/軸/大致數值是否符合宣稱；精確讀數、細格線不保證**——不確定就標「讀不清」。
- **advisory only**：這是「可疑、請人覆核」的訊號，不是「圖造假」的定論。
- 讀不到清晰圖檔（render 糊、向量太小）時，誠實說無法查核，不編。
- 定位需人或內文明確指涉「哪張圖 vs 哪個宣稱」。
