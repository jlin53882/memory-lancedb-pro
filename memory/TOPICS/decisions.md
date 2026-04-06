# 決策記錄 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/decisions.v2.md（canonical SSOT）

---

## 核心決策（精華摘要）

共 25 條決策，萃取最重要者：

### OpenClaw 維運

| ID | 決策 | 結論 | 日期 |
|----|------|------|------|
| D-2026-02-25-DAILY-UPDATE-CRON-B | 每日更新 cron | 拆成兩個 job（update+restart → verify），避免通知中斷 | 2026-02-25 |
| P-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM | Gateway restart | **必先通知家豪並等確認**，嚴禁默默重啟 | 2026-02-25 |
| D-2026-03-23-GATEWAY-RESTART-FIX | Gateway 重啟連不上 | 統一 npm 安裝路徑 | 2026-03-23 |
| D-2026-03-23-OPENCODE-ABANDONED | OpenCode TUI | 放棄，改用 exec + MiniMax | 2026-03-23 |

### 記憶系統

| ID | 決策 | 結論 | 日期 |
|----|------|------|------|
| D-2026-02-28-QMD-LANCEDB-ROLE-SPLIT | QMD 與 LanceDB 分工 | QMD 查原文（長篇 SOP/日誌）；LanceDB 存精煉結論 | 2026-02-28 |
| D-2026-02-28-MEMORY-SEARCH-MEMORY-ONLY | Memory Search | 維持 memory-only，不索引 sessions | 2026-02-28 |
| D-2026-03-23-QMD-LANCEDB-DIVISION | QMD vs LanceDB | QMD 負責索引，Lancedb 負責結論 | 2026-03-23 |
| D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG | LanceDB Pro 設定 | **三坑：絕對路徑 / apiKey 無空白 / JSON 反斜槓轉義** | 2026-03-23 |

### CLI / 批次處理

| ID | 決策 | 結論 | 日期 |
|----|------|------|------|
| P-2026-03-16-CLI-TIMEOUT-BATCH-POLICY | CLI 批次原則 | 統一 20 筆/300 秒，成功後寫 cache | 2026-03-16 |
| D-2026-03-23-CLI-TIMEOUT-300S | CLI timeout | 300s per batch 是安全閾值 | 2026-03-23 |
| D-2026-03-23-INGEST-LOCAL-PLUGIN-CLI | ingest_local.py | 改用 memory-lancedb-pro plugin CLI（避開全域套件） | 2026-03-23 |
| D-2026-03-23-MEMORY-PRO-UPGRADE-NO-LLM | memory-pro upgrade | 遇到 LLM null 時用 `--no-llm` 繞過 | 2026-03-23 |
| D-2026-03-23-BATCH-ERROR-HANDLING | 批次錯誤處理 | 錯誤不阻斷全流程，個別記錄 | 2026-03-23 |

### Sub-Agent / 執行策略

| ID | 決策 | 結論 | 日期 |
|----|------|------|------|
| P-2026-03-21-SUBAGENT-STRATEGY | Sub-Agent 策略 | >5 分鐘 / >3 件批量 / >80k context 優先拆開 | 2026-03-21 |
| P-2026-02-15-PRECISE-READING-WINDOW | 精準讀檔 | 先定位，再小窗 read | 2026-02-15 |
| P-2026-03-09-PATH-DEBUG-RECALL-FIRST | 路徑錯誤處理 | ENOENT 先 recall，再縮到單一目標驗證 | 2026-03-09 |

### James 偏好

| ID | 決策 | 結論 | 日期 |
|----|------|------|------|
| D-2026-03-23-AUTO-EXPERIENCE-LOOP | 主動模式 B | 家豪確認後主動詢問是否記錄經驗 | 2026-03-23 |
| — | 天氣查詢 | 優先使用 weather skill（Open-Meteo/wttr.in），不用 web_search/Brave | 2026-03-05 |
| — | 語言 | 繁體中文回覆，技術術語保留英文 | — |

---

## SSOT 規則

1. **`decisions.v2.md` 是唯一 canonical 決策來源**；`decisions.md` 已棄用，勿引用
2. **衝突處理**：舊決策標 `[Deprecated]` 再立新結論（SSOT）
3. **每條只存一個結論**，新舊不混在同一條
4. **必須包含**：適用版本、最後驗證日期
5. **why/根因欄只寫已驗證事實**；未驗證的推測假設一律標記 `[unverified]`

---

## 統一標記格式（所有 Agent 強制）

| 標記 | 用途 | 範例 |
|------|------|------|
| `[重要]` | 需要記住的結論、關鍵發現 | `[重要]` 使用者偏好繁體中文回覆 |
| `[設定]` | API Key、密鑰、路徑、配置 | `[設定]` dbPath: ~/.openclaw/memory/ |
| `[決策]` | 做過的決定與原因 | `[決策]` Flet 0.82.2 獨立使用 namespace |
| `[學習]` | 新學到的知識、經驗 | `[學習]` page.on_error 無法捕獲 UI handler 異常 |
| `[待追蹤]` | 未完成事項、後續行動 | `[待追蹤]` PR#22 待 James 確認後合併 |

---

## 已棄用 / 失效的決策

| 決策 | 替代方案 |
|------|---------|
| decisions.md | 改用 decisions.v2.md |
| OpenCode TUI | 改用 exec + MiniMax |
| 全域 pip 執行 ingest_local | 改用 memory-lancedb-pro plugin CLI |
