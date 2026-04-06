---
name: memory-compress
description: "Engineering-grade memory compression with dual-track output. Triggered by /compress, context > 80k tokens, major topic shift, before suggesting /reset, or session-end detection (farewell + new knowledge → prompt). Track 1: extracts permanent knowledge → LanceDB. Track 2: saves ephemeral work state → memory/active_state_<platform>.md (overwrite). Optimized for seamless /reset recovery."
---

# Memory Compress — 雙軌壓縮協議 v5.7（2026-03-09 定版）

## 觸發條件
- 使用者輸入 `/compress`
- **自動觸發**（任一即觸發）：
  1. Context 使用量估計 > 80k tokens（約 40%）
  2. 話題大幅切換且累積大量前文
  3. 即將建議使用者 `/reset` 之前
  4. 使用者出現結束語（掰掰、先這樣、等等繼續、晚點再說、我先去XXX、好了謝謝、收工、下班了等）**且**本次 session 有產生新決策、踩坑解法或環境變更
     → **不直接執行壓縮**，改為主動詢問：「⚠️ 本次 session 有新知識尚未壓縮，要執行 /compress 嗎？」

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
- **去重判斷規則**（統一）：
  - 相似度 ≥ 0.9 → 跳過（內容相同）
  - 相似度 0.75–0.9 → `memory_update`（內容更新）
  - 相似度 < 0.75 → `memory_store`（全新記憶）
  - 差異僅在「是否顯示給人確認」，規則本身保持一致
- **importance 動態調整**：
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
- **Sub-Agent 的 LanceDB 提案**（供 Main 決策）
- **低重要性記憶暫存**（v5.4 新增）

### 寫入規則
- **覆寫**（Overwrite），不是 append。永遠只保留最新一份。
- **Token 限制**：<= 800 tokens
- **裁切順序**：
  1. 先砍 `active_bugs` 的詳細描述（保留一行摘要）
  2. 再砍 `active_files` 的狀態描述（保留路徑本身）
  3. 若仍超限，砍 `pending_lancedb_proposals` 的 `reason` 欄位（只保留 text + category + importance）
  4. 若仍超限，砍 `pending_low_importance` 的條目數（v5.4 新增，最多保留 5 條；保留策略：依 `skipped_at` 排序，保留最新的 5 條，較舊的視為已過期捨棄）
  5. 最後才砍 `active_files` 的路徑（最後手段）
  6. **永遠保留**：`qmd_tags`、`resume_hint`、`pending_lancedb_proposals` 的核心欄位（text/category/importance）
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
      "reason": "Sub-Agent 觀察到的根因與價值",
      "_source_platform": "discord"
    }
  ],
  "pending_low_importance": [
    {
      "text": "低重要性記憶內容",
      "category": "fact",
      "importance": 0.6,
      "skipped_at": "YYYY-MM-DD HH:MM",
      "_source_platform": "discord"
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

**觸發模式決定掃描範圍**：

- **手動觸發**（`/compress`）：
  - 掃描當前對話歷史
  - 讀取近期 memory（今天 + 昨天的 daily md）

- **自動觸發**（context > 80k / 話題切換 / 即將 /reset；結束語偵測見觸發條件第 4 條）：
  - **只掃描當前對話歷史**
  - **不讀 daily md**（避免加重 context）

### Step 2：處理 Sub-Agent 提案

**讀取提案**：
1. 讀取 `memory/active_state_<platform>.md` 中的 `pending_lancedb_proposals`
2. 若無提案 → 跳至 Step 2b

**處理模式依觸發方式**：

#### 手動 `/compress`：人工確認（最多 3 條）
- **前 3 條**（按 importance 排序）：
  - 顯示提案內容 + reason
  - 詢問：「✅ 寫入 LanceDB / ❌ 拒絕 / ✏️ 修改後寫入」
  - 若選擇 ✏️ 修改：
    - Claw 輸出原始 text
    - 詢問：「請直接回覆修改後的完整文字」
    - 確認後以修改後的內容執行去重並寫入
  - 若選擇寫入：**先執行去重檢查**（memory_recall minScore=0.75，套用統一規則）
  - **立刻更新 active_state**：處理完一條就從 `pending_lancedb_proposals` 移除該條並寫回檔案
- **超過 3 條**：
  - importance ≥ 0.85：**先去重**（套用統一規則）後自動寫入
  - importance < 0.85：保留在 `pending_lancedb_proposals` 待複核
  - 在摘要加一行：「⚠️ 有 X 條提案自動處理，Y 條保留待複核」

#### 自動觸發：自動處理 + 記錄
- 對每條提案：
  - importance ≥ 0.85：**先執行去重檢查**（memory_recall minScore=0.75，套用統一規則），再依規則處理
  - importance < 0.85：標記「待人工複核」，保留在 `pending_lancedb_proposals`
  - **立刻更新 active_state**：寫入的移除，待複核的保留
- 完成後在摘要中列出「待人工複核」清單

### Step 2b：分類本次對話內容

將內容分為兩堆：
- **永久性**（新決策/新偏好/新踩坑解法）→ 軌道一
- **短期性**（待辦/bug/活躍檔案/上下文）→ 軌道二

### Step 3：軌道一 — 寫入 LanceDB（v5.6 修正）

對每條永久性知識執行去重檢查：

#### 手動 `/compress`：人工確認（最多 3 條）
0. **先檢查 importance**（v5.4 修正）：
   - importance ≥ 0.85 → 繼續下方去重流程
   - importance < 0.85 → **寫入 `pending_low_importance`**，跳過此條
     - 格式：`{ text, category, importance, skipped_at, _source_platform }`
1. **`memory_recall` 檢查**（使用嚴格 **minScore=0.75** 僅用於去重判斷，只對 importance ≥ 0.85 的條目執行）
2. 若召回到相似條目：
   - **前 3 條**（按 importance 排序）：
     - 顯示舊條目內容
     - 詢問：「⏭️ 跳過（相同）/ ✏️ 更新（內容變更）/ ➕ 新增（完全不同）」
   - **超過 3 條**：套用統一去重規則自動處理
     - 相似度 ≥ 0.9 → 跳過
     - 相似度 0.75–0.9 → `memory_update`
     - 相似度 < 0.75 → `memory_store`
3. 若未召回相似條目（全新記憶）→ 直接 `memory_store`（套用 importance 動態調整值）

完成後在摘要加一行：「⚠️ 有 X 條記憶自動處理，Z 條低重要性暫存待複核」

#### 自動觸發：全自動處理（v5.5 修正）
1. **先檢查 importance**（v5.5 修正，與手動模式一致）：
   - importance < 0.85 → **寫入 `pending_low_importance`**（含 `_source_platform`），跳過此條
   - importance ≥ 0.85 → 繼續下方去重流程
2. **`memory_recall` 檢查**（minScore=0.75，只對 importance ≥ 0.85 的條目執行）：
   - 若召回到相似條目 → 套用統一去重規則
     - 相似度 ≥ 0.9 → 跳過
     - 相似度 0.75–0.9 → `memory_update`
     - 相似度 < 0.75 → `memory_store`
   - 若未召回相似條目（全新記憶）→ 直接 `memory_store`
3. 完成後在摘要列出處理統計：「✅ LanceDB: X 條，⚠️ Y 條低重要性暫存」

**完成輸出**（標準格式）：
```
✅ LanceDB: 5 條（新增 3 / 更新 1 / 跳過 1）
⚠️ 2 條低重要性暫存待複核
```

### Step 4：軌道二 — 覆寫 active_state_<platform>.md

- 組裝 JSON 快照（含最新的 `pending_lancedb_proposals` + `pending_low_importance`）
- 驗證 <= 800 tokens（超出時按 v5.4 裁切順序處理）
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

**標準格式**：

```
📦 Memory Compress 完成（auto-compress | /compress）
✅ LanceDB: 5 條（新增 3 / 更新 1 / 跳過 1）
⚠️ 2 條低重要性暫存待複核
✅ active_state_discord.md 已覆寫
📝 daily md 追加：[Compress] 主題：Brave Search 參數優化 + GitHub 追蹤設定
⚠️ pending_lancedb_proposals: 2 條等待人工複核（如有）
💡 建議：/reset
```

**自動觸發時額外建議**：
- 建議使用者 `/reset`

---

## Session Startup 連動（所有 agent 必做）

在 AGENTS.md 的 Session Startup 流程中，執行：

```
1. 讀 SOUL.md
2. 讀 USER.md
3. 讀 memory/YYYY-MM-DD.md（今天+昨天）
4. 主會話時再讀 MEMORY.md
5. LanceDB autoRecall 自動注入相關記憶
6. 依平台讀取短期狀態檔（若存在）→ 載入工作進度
   - Discord：`memory/active_state_discord.md`
   - Telegram：`memory/active_state_tg.md`
   - fallback：`memory/active_state.md`
7. 檢查待處理項目
   - 若 `pending_lancedb_proposals` 非空 → 輸出：
     「⚠️ 有 N 條 Sub-Agent LanceDB 提案待決策，輸入 /review-proposals 查看」
   - 若 `pending_low_importance` 非空 → 輸出：
     「⚠️ 有 N 條低重要性記憶暫存，輸入 /review-low-importance 查看」
```

Agent 醒來後的完整狀態：
- **性格與規矩** ← LanceDB autoRecall + SOUL.md + AGENTS.md
- **手邊工作進度** ← memory/active_state_<platform>.md
- **待決策提案** ← pending_lancedb_proposals（自動提醒）
- **待複核記憶** ← pending_low_importance（自動提醒）
- **完整無縫接軌** ✅

---

## 新增指令：/review-proposals

**用途**：查看並處理待決策的 Sub-Agent LanceDB 提案

**執行流程**：
1. **判斷 platform**：
   - 依當前請求來源判斷 platform（Discord→`discord` / Telegram→`tg`）
   - 若無法判斷 → **兩個檔案都讀**，合併 `pending_lancedb_proposals` 後處理
     - 若同一條 text 重複出現，取 importance 較高者
     - **記錄每條提案的來源平台**（從 `_source_platform` 欄位或檔案來源）
   - 均無則報告：「❌ 找不到 active_state 檔案」
2. 讀取並合併 `pending_lancedb_proposals`
3. 逐條顯示：
   ```
   [1/3] Sub-Agent 提案（來源：Discord）
   內容：[群組名稱] 建議寫入的內容
   分類：decision
   重要性：0.85
   理由：Sub-Agent 觀察到的根因與價值
   
   決定：✅ 寫入 / ❌ 拒絕 / ✏️ 修改
   ```
4. 若選擇 ✏️ 修改：
   - Claw 輸出原始 text
   - 詢問：「請直接回覆修改後的完整文字」
   - 確認後以修改後的內容執行去重並寫入
5. 若選擇寫入：**先執行去重檢查**（memory_recall minScore=0.75，套用統一規則）
6. **每處理完一條**：
   - 從該條提案的**來源平台** active_state 中移除
   - 立刻更新該平台的 active_state 檔案
   - 若無法判斷來源 → **兩個平台都更新**（移除該條提案）
7. 全部處理完後輸出：「✅ 所有提案已處理」

---

## 新增指令：/review-low-importance

**用途**：查看並處理暫存的低重要性記憶

**執行流程**：
1. **判斷 platform**（同 `/review-proposals`）
2. 讀取並合併 `pending_low_importance`
3. 逐條顯示：
   ```
   [1/5] 低重要性記憶（暫存於：2026-03-09 01:30，來源：Discord）
   內容：記憶內容
   分類：fact
   重要性：0.6
   
   決定：✅ 寫入 LanceDB / ❌ 刪除 / ⏸️ 保留待定
   ```
4. 若選擇寫入：**先執行去重檢查**（memory_recall minScore=0.75，套用統一規則）
5. 每處理完一條：從該條的 `_source_platform` 對應的 active_state 中移除並更新檔案；若無法判斷來源 → 兩個平台都更新
6. 全部處理完後輸出：「✅ 所有低重要性記憶已處理」

---

## 安全規則

- **軌道一（LanceDB）**：遵守 autoCapture 煞車規則（寧可漏記絕不亂記）
- **軌道二（active_state）**：覆寫模式，永遠只保留最新一份，不累積垃圾
- **Sub-Agent 觸發壓縮時**：
  - 軌道二可自行執行
  - 軌道一的新知識寫入 `pending_lancedb_proposals`（含 reason + `_source_platform`）
  - Main 在下次 `/compress` 的 Step 2 或 `/review-proposals` 處理這些提案
- **中途中斷保護**：
  - Step 2 和 Step 3 的每條處理完立刻寫回 active_state
  - 避免中斷後重複詢問或丟失處理進度
- **去重一致性**：
  - 所有寫入 LanceDB 的路徑（Step 2 proposals / Step 3 新知識 / `/review-proposals` / `/review-low-importance`）統一先執行去重檢查
  - 去重規則統一：≥0.9 跳過 / 0.75-0.9 更新 / <0.75 新增
  - 避免任何繞過去重的直接寫入
- **importance 門檻一致性**（v5.4 完整統一）：
  - Step 2 和 Step 3 的「超出人工確認上限」或「自動觸發」時，**統一用 importance ≥ 0.85 決定是否自動處理**
  - 低於 0.85 的記憶/提案**寫入 `pending_low_importance` 或保留在 `pending_lancedb_proposals`**，不自動寫入 LanceDB，也不直接丟棄
  - 提供 `/review-low-importance` 讓使用者稍後手動決定

---

## 最近修正摘要

> 完整歷史見 `CHANGELOG.md`

- **v5.7**：新增第四觸發條件——偵測結束語且有新知識時主動提醒 `/compress`，防止知識錯覺

---

**定版時間**：2026-03-09  
**版本**：v5.7（穩定版）  
**向下相容性**：完全相容 v5.6 及以下，無新增欄位  
**建議升級**：所有使用 v4-v5.6 的環境建議升級至 v5.7
