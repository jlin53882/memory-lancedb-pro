---
name: memory-compress
description: "Engineering-grade memory compression with dual-track output. Triggered by /compress, context > 80k tokens, major topic shift, or before suggesting /reset. Track 1: extracts permanent knowledge → LanceDB. Track 2: saves ephemeral work state → memory/active_state_<platform>.md (overwrite). Optimized for seamless /reset recovery."
---

# Memory Compress — 雙軌壓縮協議 v5（2026-03-09 定版）

> **v5 更新**：
> - 🔴 新增 Sub-Agent 提案收件機制（`pending_lancedb_proposals`）
> - 🔴 自動觸發時不讀 daily md（避免加重 context）
> - 🟡 優化裁切順序（保護 active_files 路徑）
> - 🟡 memory_recall 去重使用嚴格 minScore=0.75
> - 🟡 importance 加影響範圍動態調整
> - 🟢 標準化壓縮摘要輸出格式

## 觸發條件
- 使用者輸入 `/compress`
- **自動觸發**（任一即觸發）：
  1. Context 使用量估計 > 80k tokens（約 40%）
  2. 話題大幅切換且累積大量前文
  3. 即將建議使用者 `/reset` 之前

## 核心原則：雙軌分流，長短分離

> **LanceDB 只放真理，active_state 只放進度。絕不混裝。**

---

## 軌道一：永久性知識 → LanceDB

### 提取對象
- ✅ 本次對話中**新確立**的系統偏好、架構決策
- ✅ 踩坑後確定的解決方案（根因 + 修法的**短結論**）
- ✅ 環境變更（新裝了什麼、改了什麼設定）

### 不提取
- ❌ 待辦清單、未解 bug、活躍檔案（這些是短期狀態，走軌道二）
- ❌ 討論過程、未定案草稿、玩笑話

### 寫入規則
- **加標籤**：`[Global]`（通用）或 `[群組名稱]`（專屬）
- **去重**：寫入前先 `memory_recall` 檢查（**使用嚴格 minScore=0.75** 避免重複記憶）
  - 召回到相似條目時，顯示給 Claw 人工確認是更新還是新增
  - 確認後：相同 → 跳過；內容更新 → `memory_update`；完全新增 → `memory_store`
- **importance 動態調整**（v5 新增）：
  - 基礎值：決策/踩坑 = 0.9，偏好 = 0.85，一般事實 = 0.7
  - 影響範圍修正：
    - `[Global]`（全系統）→ +0.0
    - `[群組名稱]`（單一 agent）→ -0.05
    - 單次任務（non-recurring）→ -0.1
  - 範例：全域架構決策 = 0.9，Sub-Agent 專屬調整 = 0.8，一次性事實 = 0.6

### 範例輸出
```
memory_store({
  text: "[Global] Brave Search 繁中參數：search_lang=zh-hant + ui_lang=zh-TW，不可用 zh 或 en 不帶區域",
  category: "decision",
  importance: 0.9  // Global 決策，基礎 0.9 + 0.0 = 0.9
})
```

---

## 軌道二：短期工作快照 → memory/active_state_<platform>.md（覆寫）

> <platform> 依請求來源：Discord→`discord`、Telegram→`tg`。

### 儲存對象
- 活躍檔案（正在改的檔案 + 狀態）
- 待辦清單（含具體路徑/指令）
- 未解 bug（錯誤訊息 + 定位線索）
- 當前上下文（一句話總結「現在在幹嘛」）
- **【v5 新增】Sub-Agent 的 LanceDB 提案**（供 Main 決策）

### 寫入規則
- **覆寫**（Overwrite），不是 append。永遠只保留最新一份。
- **Token 限制**：<= 800 tokens
- **裁切順序**（v5 優化）：
  1. 先砍 `active_bugs` 的詳細描述（保留一行摘要）
  2. 再砍 `active_files` 的狀態描述（保留路徑本身）
  3. 最後才砍 `active_files` 的路徑（最後手段）
  4. `qmd_tags` 和 `resume_hint` **永遠保留**
- 格式：結構化 JSON（見下方）

### 輸出格式（memory/active_state_discord.md / memory/active_state_tg.md）

```markdown
# Active State（自動產生，勿手動編輯）
> 最後更新：YYYY-MM-DD HH:MM (Asia/Taipei)
> 觸發方式：/compress | auto-compress

\```json
{
  "current_status": "一句話總結現在在幹嘛",
  "active_files": [
    "path/to/file.py (狀態：修改中/待測試/已完成)"
  ],
  "pending_tasks": [
    "[WRITE_CODE] path/to/file — 具體要做什麼",
    "[RUN_TERMINAL] 具體指令"
  ],
  "active_bugs": [
    "錯誤描述 + 定位線索（若無留空陣列）"
  ],
  "pending_lancedb_proposals": [
    {
      "text": "[群組名稱] 建議寫入的內容",
      "category": "decision",
      "importance": 0.85,
      "reason": "Sub-Agent 觀察到的根因與價值"
    }
  ],
  "qmd_tags": ["專案唯一識別詞"],
  "resume_hint": "下次接續時，建議先做什麼"
}
\```
```

### 絕對不寫入 LanceDB
這份快照是「易腐品」，下次壓縮就會被覆蓋。不可進入向量記憶。

---

## 執行流程（壓縮時依序執行）

### Step 1：掃描

**觸發模式決定掃描範圍**（v5 修正）：

- **手動觸發**（`/compress`）：
  - 掃描當前對話歷史
  - 讀取近期 memory（今天 + 昨天的 daily md）

- **自動觸發**（context > 80k / 話題切換 / 即將 /reset）：
  - **只掃描當前對話歷史**
  - **不讀 daily md**（避免加重 context）

### Step 2：分類

**優先處理 Sub-Agent 提案**（v5 新增）：
1. 讀取 `memory/active_state_<platform>.md` 中的 `pending_lancedb_proposals`
2. 對每條提案：
   - 顯示提案內容 + reason
   - 詢問：「寫入 LanceDB / 拒絕 / 修改後寫入」
   - 決定後從 `pending_lancedb_proposals` 移除該條

**分類本次對話內容**：
將內容分為兩堆：
- **永久性**（新決策/新偏好/新踩坑解法）→ 軌道一
- **短期性**（待辦/bug/活躍檔案/上下文）→ 軌道二

### Step 3：軌道一 — 寫入 LanceDB

對每條永久性知識：
1. **`memory_recall` 檢查**（使用嚴格 **minScore=0.75** 僅用於去重判斷）
2. 召回到相似條目時：
   - 顯示舊條目內容
   - 詢問：「跳過（相同）/ 更新（內容變更）/ 新增（完全不同）」
3. 執行對應操作：
   - 跳過 → 不處理
   - 更新 → `memory_update`
   - 新增 → `memory_store`（套用 importance 動態調整規則）

**完成輸出**（v5 標準格式）：
```
✅ LanceDB: 5 條（新增 3 / 更新 1 / 跳過 1）
```

### Step 4：軌道二 — 覆寫 active_state_<platform>.md

- 組裝 JSON 快照（含 `pending_lancedb_proposals` 欄位）
- 驗證 <= 800 tokens（超出時按 v5 裁切順序處理）
- **覆寫**
  - Discord：`memory/active_state_discord.md`
  - Telegram：`memory/active_state_tg.md`

**完成輸出**：
```
✅ active_state_discord.md 已覆寫
```

### Step 5：追加 daily md（可選）

- 如果本次壓縮產出了軌道一的新知識，在 `memory/YYYY-MM-DD.md` 追加一行摘要
- 格式：`- [Compress] 新增 N 條 LanceDB 記憶（主題：...）`

### Step 6：輸出壓縮摘要

**標準格式**（v5 定義）：

```
📦 Memory Compress 完成（auto-compress | /compress）
✅ LanceDB: 5 條（新增 3 / 更新 1 / 跳過 1）
✅ active_state_discord.md 已覆寫
📝 daily md 追加：[Compress] 主題：Brave Search 參數優化 + GitHub 追蹤設定
⚠️ pending_lancedb_proposals: 2 條等待 Main 決定（如有）
💡 建議：/reset
```

**自動觸發時額外建議**：
- 建議使用者 `/reset`

---

## Session Startup 連動（所有 agent 必做）

在 AGENTS.md 的 Session Startup 流程中，新增：

```
1. 讀 SOUL.md
2. 讀 USER.md
3. 讀 memory/YYYY-MM-DD.md（今天+昨天）
4. 主會話時再讀 MEMORY.md
5. LanceDB autoRecall 自動注入相關記憶
6. 【v4 新增】依平台讀取短期狀態檔（若存在）→ 載入工作進度
   - Discord：`memory/active_state_discord.md`
   - Telegram：`memory/active_state_tg.md`
   - fallback：`memory/active_state.md`
7. 【v5 新增】檢查 pending_lancedb_proposals
   - 若有 Sub-Agent 提案，在適當時機提醒 Main 處理
```

Agent 醒來後的完整狀態：
- **性格與規矩** ← LanceDB autoRecall + SOUL.md + AGENTS.md
- **手邊工作進度** ← memory/active_state_<platform>.md
- **待決策提案** ← pending_lancedb_proposals
- **完整無縫接軌** ✅

---

## 安全規則

- **軌道一（LanceDB）**：遵守 autoCapture 煞車規則（寧可漏記絕不亂記）
- **軌道二（active_state）**：覆寫模式，永遠只保留最新一份，不累積垃圾
- **Sub-Agent 觸發壓縮時**（v5 明確定義）：
  - 軌道二可自行執行
  - 軌道一的新知識寫入 `pending_lancedb_proposals`（含 reason）
  - Main 在下次 `/compress` 的 Step 2 優先處理這些提案

---

## v5 優化總表

| 優先級 | 問題 | v5 修正 |
|--------|------|---------|
| 🔴 | Sub-Agent 提案無收件機制 | 新增 `pending_lancedb_proposals` 欄位 + Step 2 處理流程 |
| 🔴 | 自動觸發時讀 daily md 加重 context | Step 1 分手動/自動兩種模式，自動時不讀 daily md |
| 🟡 | 裁切順序保護錯誤 | 改為先砍 bugs → files 狀態 → files 路徑 |
| 🟡 | memory_recall 去重精準度不足 | Step 3 使用嚴格 minScore=0.75 + 人工確認 |
| 🟡 | importance 靜態分布 | 加影響範圍修正（Global/群組/單次） |
| 🟢 | 壓縮摘要無標準格式 | Step 6 定義完整輸出格式 |
| 🟢 | description 觸發條件不完整 | frontmatter 補完所有觸發條件 |

---

**定版時間**：2026-03-09  
**向下相容性**：完全相容 v4，新增欄位向下兼容（舊版 active_state 沒有 `pending_lancedb_proposals` 時視為空陣列）
