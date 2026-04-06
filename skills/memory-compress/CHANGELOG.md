# Memory Compress — 完整優化歷史（v4 → v5.7）

| 版本 | 優先級 | 問題 | 修正 |
|------|--------|------|------|
| v5 | 🔴 | Sub-Agent 提案無收件機制 | 新增 `pending_lancedb_proposals` 欄位 + Step 2 處理流程 |
| v5 | 🔴 | 自動觸發時讀 daily md 加重 context | Step 1 分手動/自動，自動時不讀 daily md |
| v5 | 🟡 | 裁切順序保護錯誤 | 改為先砍 bugs → files 狀態 → files 路徑 |
| v5 | 🟡 | memory_recall 去重精準度不足 | Step 3 使用嚴格 minScore=0.75 |
| v5 | 🟡 | importance 靜態分布 | 加影響範圍修正（Global/群組/單次） |
| v5 | 🟢 | 壓縮摘要無標準格式 | Step 6 定義完整輸出格式 |
| v5 | 🟢 | description 觸發條件不完整 | frontmatter 補完所有觸發條件 |
| v5.1 | 🔴 | 自動觸發時「詢問」卡住流程 | Step 2/3 分手動/自動，自動時套預設規則 |
| v5.1 | 🔴 | Proposal 中途中斷不寫回 | 每處理完一條立刻更新 active_state |
| v5.1 | 🟡 | Session Startup「適當時機」未定義 | 明確為 startup 完成後提醒 + `/review-proposals` |
| v5.1 | 🟡 | 人工確認無數量上限 | Step 3 手動模式最多確認 3 條 |
| v5.1 | 🟢 | v5 changelog 消耗 token | 移除頂部 changelog |
| v5.2 | 🔴 | proposals 自動寫入繞過去重 | Step 2 自動寫入前先執行去重檢查 |
| v5.2 | 🟡 | 0.75–0.85 區間規則不一致 | 統一去重規則：≥0.9 跳過 / 0.75-0.9 更新 / <0.75 新增 |
| v5.2 | 🟡 | `/review-proposals` platform 未定義 | 明確定義 platform 判斷邏輯（來源→discord/tg→fallback） |
| v5.2 | 🟢 | Step 2 手動確認無數量上限 | 手動模式最多 3 條，超出依 importance 自動處理 |
| v5.3 | 🟡 | proposals 不在裁切順序 | 裁切順序加入 proposals 的 reason 欄位處理規則 |
| v5.3 | 🟡 | Step 3 超出 3 條缺 importance 門檻 | importance ≥ 0.85 自動處理，< 0.85 跳過 |
| v5.3 | 🟢 | 修改流程未定義 | 明確「✏️ 修改」= 輸出原文 + 詢問修改後文字 + 去重寫入 |
| v5.3 | 🟢 | fallback 雙平台漏讀 | `/review-proposals` fallback 改為合併雙平台 proposals |
| v5.4 | 🟡 | Step 3 自動觸發缺 importance 門檻 | 自動觸發加 importance 分流：≥0.85 寫入，<0.85 暫存 |
| v5.4 | 🟡 | `pending_low_importance` 缺 `_source_platform` | 結構加入 `_source_platform` 欄位 |
| v5.4 | 🟡 | 手動模式全新記憶缺 importance 篩選 | importance 檢查前置於 memory_recall 之前 |
| v5.4 | 🟢 | `/review-proposals` fallback 寫回邏輯不明確 | 記錄來源平台（`_source_platform`），寫回時更新正確檔案 |
| v5.4 | 🟢 | Step 3 低重要性記憶靜默丟棄 | 新增 `pending_low_importance` 暫存 + `/review-low-importance` |
| v5.4 | 🟢 | 裁切保留哪 5 條未定義 | 明確依 `skipped_at` 保留最新 5 條 |
| v5.4 | 🟢 | 歷史表佔用 token | 歷史表移至 `CHANGELOG.md`，SKILL.md 只保留最近版摘要 |
| v5.5 | 🟢 | 自動觸發 memory_recall 順序低效 | importance 篩選前置於 memory_recall 之前（與手動一致） |
| v5.5 | 🟢 | 手動模式全新記憶路徑未明確 | 補全「未召回相似條目 → 直接 memory_store」路徑 |
| v5.6 | 🟡 | 「若未召回」縮排錯位在「若召回」子層級 | 拉出為獨立平行分支（手動 Step 3 + 自動 Step 2） |
| v5.6 | 🟢 | Step 3 header 仍標 v5.4 | 更新為 v5.6 |
| v5.6 | 🟢 | Session Startup 內嵌版本標注未同步 | 移除內嵌版本號 |
| v5.6 | 🟢 | v5.4 摘要未移出正文 | 最近摘要只保留最新版 |
| v5.7 | 🟡 | 大多數 session 不觸發自動壓縮（知識錯覺風險） | 新增第四觸發條件：結束語 + 有新知識 → 主動提醒 /compress；AGENTS.md 加結束語偵測規則 |
