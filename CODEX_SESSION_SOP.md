# Codex Session 複用 SOP

> 本 SOP 旨在建立 Codex 長期 session 複用機制，讓每次 coding 都建立在過去的基礎上，而非從零開始。

## 背景

目前每次 Coding 任務都是新的 Codex session，沒有累積。長期下來 agent 對專案的理解無法疊加，導致：
- 每次都要重新說明專案架構
- 無法延續上次未完成的工作
- 上下文喪失造成的重複勞動

## 目標

建立 Codex 長期 session 複用機制，達成：
1. 跨工作天維持同一 session，掌握專案上下文
2. session 閒置超過 24 小時才建立新的
3. 每次開始工作前自動摘要進度，接續執行

---

## 機制設計

### Session 命名規範

```
codex-{專案名}-{日期}
```

**範例**：
- `codex-two_project-20260325`
- `codex-ftb_snbt-20260324`

### 何時建立新 session vs 複用

| 情境 | 動作 |
|------|------|
| 每個工作天第一個 coding 任務 | 建立或複用當天的 session |
| 工作天中途的 coding 任務 | 複用當前活跃 session |
| 超過 24 小時的閒置 | 建立新的 session |
| 需要清理時（session 過於龐大）| 標記舊 session 為 archive，另開新的 |

**判斷邏輯**：
```
IF 今天沒有適用的 session AND距離上次使用 < 24小時
  → 複用現有 session
ELIF 距離上次使用 >= 24小時
  → 建立新的 session（命名含今天日期）
ELIF session 過於龐大（> 50 條消息）
  → archive 舊的，建立新的
```

### 如何傳遞上下文

#### 1. Session 啟動時（自動執行）
```
1. 讀取相關的 PROJECT_*.md（位於 workspace/）
2. 若有 memory/codex_progress_*.md，摘要上次進度
3. 將摘要作為 system prompt 的一部分帶入 session
```

#### 2. 工作開始前（Agent 自動執行）
```
1. 詢問或讀取：「上次做到哪裡？」
2. 摘要进度を口語化陳述
3. 確認本次目標
```

#### 3. 工作結束後（Agent 自動執行）
```
1. 寫入進度到 memory/codex_progress_{專案名}.md
2. 格式：[時間] {完成內容} → [下一步]
3. 若有錯誤/踩坑，寫入 .learnings/
```

### 在 AGENTS.md 中的觸發時機

#### 觸發關鍵字
- 「幫我寫 code」
- 「修改程式碼」
- 「實作」
- 「開 Codex」
- 任何涉及 `opencode-controller` skill 的指令

#### 觸發後的檢查流程
```
1. 檢查 memory/ 目錄是否有適用的 codex_progress_*.md
2. 若有，讀取並摘要進度
3. 檢查目前是否有活跃的 Codex session
4. 根據「何時建立新 session vs 複用」原則決定
5. 啟動 session 時帶入上下文摘要
```

---

## 實作細節

### Session 狀態追蹤

在 `memory/codex_sessions.md` 維護 session 註冊表：

```markdown
# Codex Session 註冊表

## 活跃 Session
| 專案 | Session 名稱 | 最後使用 | 消息數 |
|------|-------------|----------|--------|
| two_project | codex-two_project-20260325 | 2026-03-25 14:30 | 23 |

## 已 Archive
| 專案 | Session 名稱 | 創建日期 | 結束日期 |
|------|-------------|----------|----------|
| two_project | codex-two_project-20260324 | 2026-03-24 | 2026-03-24 |
```

### 進度寫入格式（memory/codex_progress_{專案}.md）

```markdown
# {專案名} Codex 進度

## 2026-03-25
- **已完成**：登入功能、session 管理模組
- **進行中**：測試驅動開發重構
- **待完成**：CI/CD 整合
- **踩坑**：Python 3.12 的 dataclass 行為變更需注意
```

---

## 與 Sub-Agent Policy 的整合

Codex session 複用機制**不是**獨立的，它與 Sub-Agent Policy 交互：

| 情境 | 處理方式 |
|------|----------|
| 小型 coding 任務（< 5 分鐘）| 主線直接處理，不開 Codex session |
| 大型 coding 任務（> 5 分鐘）| 開 Sub-Agent + Codex session，並寫入進度 |
| 需要創意/複雜推理 | M2.7-highspeed 或 Codex，視情況決定 |
| 多個大型任務并行 | 每批最多 3 個 Sub-Agent，每個可有獨立的 Codex session |

---

*最後更新：2026-03-25*
