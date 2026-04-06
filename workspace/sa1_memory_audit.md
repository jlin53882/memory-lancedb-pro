# SA-1 MemoryAudit 報告

**執行日期：** 2026-03-22  
**抽樣範圍：** 前 220 條記憶（LanceDB 總計 3046 條）

---

## quality_score: 45 / 100

**評分理由：**
- `decision` 佔 1597 條（52.4%），但其中大量是**完整文件 embedding** 而非實際結論，造成記憶庫嚴重膨脹
- 已發現 11 筆明確重複（相同文件重複寫入 3~5 次）
- `other` 類別夾雜大量低價值噪聲（requirements.txt、vocab_index.txt、english_practice_state.json）
- 抽樣中無 stale 記憶（最新一批是 2026-03-21，距今 1~2 天），但整體 drift 問題嚴重

---

## duplicate_ids: [共 11 筆，明確重複]

| 文件名 | 出現次數 | Memory IDs |
|--------|---------|------------|
| `SOP_EMBEDDING_MODEL_SWITCH.md` | 5 次 | `6d17b3e6-f666-48bd-8389-ce9e926b5f91`, `4e60978e-4f15-4620-8e91-a318bfc91023`, `1daf7c76-7276-4077-95c0-bb77372ac6d1`, `d155d23e-8703-4e6a-b3c9-8cbee6de8198`, `3a322d55-4222-4f7e-90aa-5457a1059cd2` |
| `minimax-model-switch-guide.md` | 3 次 | `aaf09114-ea6f-4ebd-8eb0-ff4cb4952731`, `57e7085c-2cdc-433c-9a0c-83665cec6686`, `74c1e660-ad13-4fb5-870b-c7de5d4678e8` |
| `2026-02-24-model-switch.md` | 3 次 | `dd5d7db5-3a9f-4536-9ddf-6f7d1e31c17a`, `25ab668b-5292-483f-b5e1-91de81a18252`, `4ad2fc79-767f-4886-88b0-99d1bb19b4e2` |

**說明：** 同一份文件被重複 embedding 進記憶庫，每次都是完整內容，造成 11 筆記憶佔用的空間幾乎完全重疊。

---

## noise_ids: [共 10+ 筆，低價值噪聲]

| Memory ID | 內容摘要 | 問題 |
|-----------|---------|------|
| `5e919ffd-2a95-4780-a235-d90e16479f29` | `requirements.txt: requests openpyxl python-dotenv...` | 只有一行文字，無決策價值 |
| `719fdc12-83d3-4c4d-ae56-9bf9f0ad7f48` | 同上（requirements.txt 重複） | 同上 |
| `933778f6-8479-4671-a2c9-1b1ffc7b147a` | 同上（requirements.txt 重複） | 同上 |
| `8c44af52-ee18-4465-a39d-7b7b6b47f003` | `vocab_index.txt: [EASY-TO-MIX-UP] bakery...` | 英文單字列表片段，無記憶價值 |
| `f91c11dc-7e8a-483d-9489-0a4514e71009` | `vocab_index.txt` 重複 | 同上 |
| `8b71c9d8-561a-4ab7-9c63-d80ed4b15f41` | `vocab_index.txt` 重複 | 同上 |
| `e3a4c6c6-f62f-44ac-9a6d-4053900b6e79` | `english_practice_state.json` | 狀態 JSON 檔，不應進記憶庫 |
| `5b16b6db-f7b4-43f2-85e7-b5d0fdcb8e57` | `english_practice_state.json` 重複 | 同上 |
| `94b44c86-733a-4ea4-abcb-4e0dedc14667` | `english_practice_state.json` 重複 | 同上 |
| `f5779052-cd4b-4727-a1be-915c58ca03a7` | `Conversation info (untrusted metadata)` | 未信任的 metadata，不應進記憶庫 |

**說明：** `other` 類別（總計 127 筆）大量被此類噪聲佔據，強烈建議清理。

---

## stale_ids: []

**抽樣結果：** 前 220 條記憶中，最舊的是 2026-03-18，距今約 4 天，全部都在 30 天內。  
**注意：** 此結果僅限抽樣範圍，無法斷言 3046 筆中無更舊記憶，需全量掃描才能確認。

---

## drift_report

**嚴重程度：高**

### 現狀差異

| 面向 | decisions.md | LanceDB (實際) |
|------|-------------|----------------|
| 決策數量 | ~40 條精煉結論 | 1597 條（42 倍） |
| 內容性質 | 短結論、適用版本、驗證時間 | 大量**完整文件 embedding** |
| 組織方式 | 按 D/H/G 分類（維運、開發、QMD） | 按 category 無明顯組織 |

### Drift 根因分析

1. **文件 embedding 當決策**：每次 `ingest_local.py` 把文件 embedding 後，整份 SOP/工作日誌被當成一筆 `decision` 寫入，而非只寫「結論」
   - 例：`SOP_EMBEDDING_MODEL_SWITCH.md` 被重複寫入 5 次
   
2. **Stock Trading 系統重複 embedding**：同一份 `.py` 檔案（operation_script.py、minimax_client.py 等）在 2026-03-20 和 2026-03-21 各 embedding 一次，共 2 份，佔用大量事實記憶

3. **`decisions.md` 過於精煉**：相較於 LanceDB 1597 決策，decisions.md 只有約 40 個章節，已無法作為「查閱起點」

4. **`other` 類別失控**：`vocab_index.txt`、`english_practice_state.json`、`requirements.txt` 這類動態狀態檔不應進記憶庫，但顯然有進入

---

## category_distribution_analysis

| Category | 數量 | 佔比 | 評估 |
|----------|------|------|------|
| decision | 1597 | 52.4% | ⚠️ 過高，且摻雜大量文件 embedding |
| fact | 725 | 23.8% | 合理，但有 stock code 重複問題 |
| reflection | 378 | 12.4% | 合理 |
| preference | 219 | 7.2% | 合理 |
| other | 127 | 4.2% | ⚠️ 包含大量噪聲，應清理 |

**核心問題：** `decision=1597` 的真實「結論密度」遠低於數字所示，大量是**包裝成決策的文件 embedding**，而非真正可行动的决策结论。

---

## top_decision_themes: [以 recall 驗證]

透過 `memory_recall` 以 `decision` category 搜尋高頻主題：

1. **Sub-agent 策略**（timeout 處理、數量上限 6 顆、模型分散策略）
   - 相關記憶：`ee2636bd`, `64ad4c9e`, `d3a4841f`, `ed734289`, `d4cac9c1`

2. **Embedding/模型切換**（jina-v5、SOP_EMBEDDING_MODEL_SWITCH、model switch guides）
   - 相關記憶：`6d17b3e6`, `b55ff49a`, `7d235890`, `1aa43bab`
   - 注意：同一份 SOP 被重複寫入 5 次

3. **Cron 與自動化**（cron timeout 調整、isolated session delivery）
   - 相關記憶：`d3a4841f`, `31233d84`

4. **PR / 開發流程**（PR #33 fix、audit findings、批次處理原則）
   - 相關記憶：`16338859`, `c505a35f`, `a7f9ab90`, `c0599fcb`

5. **Stock Trading 系統**（Python 防呆、API 差異、MiniMax client）
   - 相關記憶：`cb769120`, `4ac5d0b4`, `71009345`

---

## 建議清理動作

1. **刪除重複文件 embedding**（11 筆）
   - `SOP_EMBEDDING_MODEL_SWITCH.md` × 5 → 保留 1 筆
   - `minimax-model-switch-guide.md` × 3 → 保留 1 筆
   - `2026-02-24-model-switch.md` × 3 → 保留 1 筆

2. **刪除噪聲 entries**（10+ 筆）
   - 所有 `requirements.txt`、`vocab_index.txt`、`english_practice_state.json` 進記憶庫的項目
   - `Conversation info (untrusted metadata)` 項目

3. **Stock Trading 程式碼檔**（多人協作項目，建議離開記憶庫）
   - 若 Stock_trading 是獨立專案，其 `.py` 原始碼應放在版本控制，不應以 `fact` 形態進 OpenClaw 記憶庫

4. **Decisions.md 同步更新**
   - 建議將 decisions.md 擴充至涵蓋近 30 天內所有真實决策，並標注對應 LanceDB 入口

---

*本報告由 SA-1 MemoryAudit sub-agent 產生（2026-03-22）*