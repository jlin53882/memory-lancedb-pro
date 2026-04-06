# Claude Code CLI Multi-Agent Coordinator 系統深度分析

> 分析目標：`win4r/claude-code-2` — 2026-03-31 洩漏的 Anthropic Claude Code CLI 原始碼
> 分析日期：2026-04-02
> 分析工具：web_fetch 抓取 raw GitHub 內容

---

## 一、Coordinator 架構

### 1.1 定位與角色模型

Claude Code 的 Coordinator 是一種特殊的**執行模式（execution mode）**，而非獨立程序。主 agent 在 Coordinator Mode 下轉變為「協調者」，將任務拆解後派遣給 worker sub-agents，收到結果後進行綜合，最終回報給使用者。

**與 OpenClaw subagent 的核心差異**：
- OpenClaw 是「主 agent 直接派工」，結果在同個對話 context 裡可見
- Claude Code 是「主 agent 轉為 coordinator」，所有 worker 結果以 `<task-notification>` XML 標籤**打斷主 agent 的回合**強制 re-entry

### 1.2 啟動機制

由 Feature Flag `COORDINATOR_MODE` + 環境變數 `CLAUDE_CODE_COORDINATOR_MODE` 控制。Session resume 時會比對 stored mode 與當前 mode，必要時翻轉環境變數（`matchSessionMode()`）。

### 1.3 System Prompt 注入

協調者收到的 system prompt 定義於 `coordinatorMode.ts:getCoordinatorSystemPrompt()`，包含：

| 段落 | 核心內容 |
|------|---------|
| Role | 你是 coordinator，不是 worker |
| Tools | AgentTool（派遣）、SendMessageTool（繼續）、TaskStopTool（停止）|
| Workers | Async 執行，結果以 `<task-notification>` 送達 |
| 嚴禁 | 感謝 worker、fabricate agent 結果、「基於你的發現」等懶惰 delegation |
| Prompt 品質要求 | 必須包含具體檔案路徑、行號、精確 spec |

**重要設計原則**：Coordinator 的 system prompt 強制要求所有 worker prompts **自給自足（self-contained）**，因為 worker 無法看見 coordinator 的對話歷史。

### 1.4 派遣流程

```
Coordinator turn
  │
  ├── AgentTool({ subagent_type: "worker", prompt: "...自足spec..." })
  ├── AgentTool({ ... })  ← 可並行多個
  └── 回覆使用者：「正在並行調查」

User role message 夾帶 <task-notification> 送達（打斷回合）
  │
  └── Coordinator 讀取 worker 結果 → 綜合 → SendMessageTool 繼續同一 worker
                                  或 AgentTool 派遣新 worker
```

---

## 二、Multi-Agent 生命週期管理

### 2.1 Sub-agent 派遣（AgentTool）

**兩條路徑**：

#### 路徑 A：一般 sub-agent（非 fork）
- 由 `subagent_type` 指定 agent 類型（worker、explorer、plan 等）
- 獨立建構 system prompt、獨立 tools pool
- 可選 `isolation: "worktree"` 隔離：建立 git worktree，確保檔案修改不衝突
- Agent 前端定義可包含 `requiredMcpServers`，MCP 連線後才啟動（最多等 30 秒）

#### 路徑 B：Fork sub-agent（實驗性 feature `FORK_SUBAGENT`）
- `subagent_type` 省略時觸發（隱性 fork）
- Child **繼承 parent 完整對話 context**（含所有 tool_use 區塊）
- 為支援 prompt cache，所有 fork child 的 API request prefix 幾乎完全相同（僅 per-child directive 不同）
- Fork child 的 tool_results 全為相同 placeholder text（`"Fork started — processing in background"`）
- **防呆機制**：fork child 不可再 fork（`isInForkChild()` 掃描訊息中的 `<FORK_BOILERPLATE_TAG>`）
- `thinking` 預設關閉（節省 output tokens）

#### Worktree 隔離
- `isolation: "worktree"` 時，child 在 git worktree 中運作
- 注入 `buildWorktreeNotice()` 告知 child 翻譯路徑
- 若 worktree 無變更，agent 結束後自動刪除 worktree

### 2.2 Async vs. Sync 執行

| 條件 | 行為 |
|------|------|
| `run_in_background=true` | Async |
| `isCoordinatorMode=true` | **全部強制 async** |
| `FORK_SUBAGENT` feature on | 全部強制 async |
| `KAIROS` feature on + kairosEnabled | 全部強制 async |
| Proactive mode active | 全部強制 async |
| 背景任務被 `CLAUDE_AUTO_BACKGROUND_TASKS` 啟用 | 120 秒後自動背景化 |

**為何 coordinator 必須 async**：sync sub-agent 會占用主 loop 的 turn，導致排隊的 cron 任務全部被 block。

### 2.3 Sub-agent 生命週期鉤子

- `executeSubagentStartHooks`：在 agent 啟動前收集額外 context
- `registerFrontmatterHooks`：agent 專屬的 hooks（從 agent 前端定義載入）
- `startAgentSummarization`：background summarization（fork 或 coordinator 模式下啟用）
- 支援 `preload skills`：agent 前端可宣告預先載入的 skills

### 2.4 訊息傳遞：`<task-notification>` 格式

Worker 完成後，結果以如下 XML 送達（格式為 user role message）：

```xml
<task-notification>
<task-id>{agentId}</task-id>
<status>completed|failed|killed</status>
<summary>Agent "描述" completed</summary>
<result>{agent 的最終文字回覆}</result>
<usage>
  <total_tokens>N</total_tokens>
  <tool_uses>N</tool_uses>
  <duration_ms>N</duration_ms>
</usage>
</task-notification>
```

- `<result>` 和 `<usage>` 是 optional
- Coordinator 以 `<task-notification>` 的 opening tag 區分這不是一般 user message
- Worker 失敗時，Coordinator **繼續同一 worker**（`SendMessageTool`），因為它有完整錯誤 context

### 2.5 Team 生命週期

#### TeamCreateTool
- 建立 `TeamFile`（JSON，存在磁碟）
- 包含：`name`、`leadAgentId`、`members[]`（扁平陣列）
- 成員屬性：`agentId`、`name`、`agentType`、`model`、`joinedAt`、`tmuxPaneId`、`cwd`、`subscriptions[]`、`isActive`
- Reset task list 目錄（以 team name 作為 task list ID）
- 限制：一個 leader 只能擁有一個 team

#### TeamDeleteTool
- 檢查 `isActive !== false` 的成員數量
- 若有活躍成員 → 拒絕刪除，要求先 `requestShutdown`
- 清理：team 目錄、worktrees、color assignments、task list

#### 成員註冊時間點
1. `spawnTeammate()` 在 tmux/iTerm2 split pane 中啟動程序
2. 初始指令透過 `writeToMailbox()` 傳遞（inbox polling 機制）
3. 註冊到 `AppState.teamContext.teammates` map
4. 寫入 teamFile磁碟

---

## 三、通訊模型

### 3.1 核心訊息架構：Mailbox System

所有 team 成員間訊息透過 `writeToMailbox()` 持久化到磁碟。收件方透過 polling 或 event 接收。

**訊息類型**：
- **一般訊息**：`{ from, text, summary, timestamp, color }`
- **廣播**：`to: "*"` → 遍历 teamFile.members，排除發送者
- **Shutdown Request**：`{ type: "shutdown_request", requestId, from, reason }`
- **Shutdown Response**：`{ type: "shutdown_response", requestId, approve: boolean, reason? }`
- **Plan Approval/Rejection**：`{ type: "plan_approval_response", requestId, approved: boolean, feedback? }`

### 3.2 SendMessageTool 路由邏輯

- `to: <name>` → 單一收件者（查 `agentNameRegistry` 或 teamFile）
- `to: *` → 廣播
- `to: "uds:<socket>"` → Unix Domain Socket peer
- `to: "bridge:<session>"` → Remote Control peer（跨機器，**需要 explicit consent**）
- In-process teammate 收到 shutdown → 直接 `abortController.abort()`
- Out-of-process teammate 收到 shutdown → 寫 mailbox + `gracefulShutdown(0)`

### 3.3 共享上下文機制

#### Scratchpad Directory（跨 worker 知識共享）
協調者可指定 `scratchpadDir`，所有 worker 對該目錄有讀寫權限且無 permission prompt。用於「持久化跨 worker 的共享知識」。

#### Agent Memory（三層隔離範圍）
| Scope | 路徑 | 用途 |
|-------|------|------|
| `user` | `~/.claude/agent-memory/<agentType>/` | 跨專案通用學習 |
| `project` | `<cwd>/.claude/agent-memory/<agentType>/` | 專案內共享（進 VCS）|
| `local` | `<cwd>/.claude/agent-memory-local/<agentType>/` | 本機專用（不进 VCS）|

Memory 以 `MEMORY.md` 為入口，agent 啟動時載入作為 system prompt 的一節。

#### Fork Context（fork sub-agent 專用）
Fork child 接收 parent 的完整 conversation history（所有 assistant messages 含 tool_use 區塊）。透過 `buildForkedMessages()` 建構：將 parent 的 assistant message 完整 clone，再接一個 user message（內含所有 tool_use 的 placeholder results + per-child directive）。

---

## 四、隔離機制分析

### 4.1 Workspace / Scope 隔離

Claude Code **沒有等同於 OpenClaw 的 workspace/scope 隔離**。它的隔離機制是：

| 機制 | 說明 |
|------|------|
| **git worktree** | `isolation: "worktree"` 在獨立目錄複製 repo，有變更才保留 |
| **cwd 覆寫** | `cwd` 參數改變 agent 的 `getCwd()` 傳回值 |
| **MCP 隔離** | Agent 可自帶 frontmatter MCP servers（additive to parent）|
| **file state cache** | Fork child clone parent's file state cache，worktree child 有獨立 cache |
| **transcript 分組** | `transcriptSubdir` 將 subagent  transcript 寫入子目錄 |

**對比 OpenClaw**：
- OpenClaw 的 workspace scope 是 session-level 隔離
- Claude Code 的 scope 隔離主要基於**程序邊界**（tmux panes / iTerm2 split panes / in-process）
- **沒有類似 OpenClaw 三層記憶架構（LanceDB）的 semantic memory 隔離**

### 4.2 許可權隔離

- Sub-agent 的 tools pool 由 `assembleToolPool(workerPermissionContext)` 獨立建構
- `workerPermissionContext` 是 parent permission context 的 copy，但 mode 可被 agent 前端定義覆寫
- `allowedTools` 參數可限制 agent 只能使用特定 tools（session-level allowlist）
- **bubble mode**：sub-agent 的 permission prompt 冒泡到 parent terminal（不阻斷 sub-agent 本身）
- In-process teammate **不能** spawn background agents（lifecycle 綁定於 leader process）

### 4.3 團隊成員隔離

- **扁平 roster**：`teamFile.members` 是扁平陣列，沒有巢狀結構
- 限制：成員不能 spawn 其他成員（`isTeammate() && teamName && name` → Error）
- In-process teammate 不能 spawn background agents
- Shutdown 是**協商式**（需要成員回應 `shutdown_response`），不是強制中斷

---

## 五、與 OpenClaw 的架構對照

| 維度 | Claude Code | OpenClaw（對照）|
|------|------------|----------------|
| 主從關係 | Coordinator 模式，agent 自帶完整 system prompt | 主 agent 直接派工，sub-agent 用 sessions_spawn |
| 訊息傳遞 | Mailbox（磁碟）+ re-entry via `<task-notification>` | sessions/history polling 或 direct reply |
| 團隊管理 | TeamFile（磁碟）+ 持久化成員狀態 | 目前無對應 |
| 背景任務追蹤 | `registerAsyncAgent` + `agentBackgroundTask` object | sessions_list / subagents tool |
| 錯誤處理 | 繼續同一 worker（SendMessage）vs 重新 spawn | 目前無明確機制 |
| 記憶共享 | Scratchpad目錄 + Agent Memory（user/project/local scope） | LanceDB 三層架構 |
| 隔離單位 | 程序邊界（tmux/iTerm2/in-process）| 目前無對應 |
| Worktree | 有（`isolation: "worktree"`）| 目前無對應 |
| 並行控制 | Read-only 可並行；Write 需序列化 | 目前無明確控制 |

---

## 六、可借鑒到 OpenClaw 的設計

### 6.1 Prompt 自給自足原則（高價值）

> **借鑒點**：每次派工必須是完整、具體的 spec，包含檔案路徑、行號、精確行為描述。

Claude Code 禁止「基於你的發現」這類 delegation，因為 worker 無法看見 coordinator 的對話。這個設計很適合 OpenClaw 的 sub-agent 派工場景。

**具體做法**：
- 派工前，agent 必須先綜合研究結果
- Prompt 包含：目標檔案、精確行號、預期行為、「完成」的定義
- 壞範例：`"基於研究，實作 auth"` → 好範例：`"在 src/auth/validate.ts:42 的 confirmTokenExists 函式中，在 user.id 存取前加 null check，若 null 回 401"`

### 6.2 Worker 生命週期：Continue vs. Spawn 判斷表（高價值）

| 情境 | 機制選擇 |
|------|---------|
| 研究探索的檔案 = 需編輯的檔案 | **Continue**（SendMessage）|
| 研究範圍廣，實作範圍窄 | **Spawn fresh** |
| 修正失敗 | **Continue**（有錯誤 context）|
| 驗證別人剛寫的程式碼 | **Spawn fresh**（保持懷疑）|
| 第一次嘗試方向錯誤 | **Spawn fresh**（避免錨定效應）|

### 6.3 Async-first 架構（中等價值）

協調者全部走 async，讓 cron 與使用者輸入能繼續處理。適用於 OpenClaw 的 `sessions_spawn` 模式。

### 6.4 三層 Agent Memory 命名空間（中等價值）

`user / project / local` 三個 scope 的 memory 隔離，可以借鑒到 OpenClaw 的 LanceDB memory 組織。

### 6.5 Shutdown 協商 protocol（中等價值）

結構化的 `shutdown_request → shutdown_response` 訊息，比簡單的中斷訊號更乾淨。適用於 OpenClaw 的 sub-agent 優雅退出。

### 6.6 TeamFile 持久化（低～中價值）

將團隊狀態寫入磁碟，session resume 時可恢復。OpenClaw 目前無團隊概念，但這個 persistent team state 的想法適用於 sub-agent 的 session 恢復。

---

## 七、潛在風險

### 7.1 扁平 roster 導致複雜度上限低

團隊成員是扁平陣列，無巢狀从屬關係。當 agent 數量增加時，coordinator 需要手動追蹤所有成員狀態，難以擴展到真正的大型多 agent 系統。

**風險**：協調子需要知道所有成員名稱，隨成員數量增加，coordinator 的管理工作線性成長。

### 7.2 Shutdown 依賴成員合作

成員收到 `shutdown_request` 後若不回應 `shutdown_response`，`TeamDeleteTool` 會拒絕刪除 team，導致 team 變成「幽靈團隊」（磁碟狀態殘留）。

**緩解**：有 `isActive !== false` 檢查，但成員 crash 時 `isActive` 狀態更新時機不明確。

### 7.3 Fork Path 的 Prompt Cache 假設脆弱

Fork child 的 API request prefix 幾乎完全相同依賴於：所有 tool_results 都是同一個 placeholder text。這意味著任何在 fork 前改變 parent API response format 的變更，都可能破壞 cache 有效性。comment 本身也承認這是 fragile 的。

### 7.4 Scratchpad 共享導致隐含耦合

若 `scratchpadDir` 被多個 worker 並行寫入，沒有任何協作機制（如檔案鎖），可能導致寫衝突或資料覆蓋。

### 7.5 過度依賴 System Prompt 注入

Coordinator 的行為規則（Section 1-6）全在 system prompt 中定義，無 code-level 強制。Sub-agent 可以通过 prompt injection 覆寫其行為（如忽視「不要 spawn sub-agent」的規則）。

### 7.6 In-process Teammate 的 Lifecycle 耦合

In-process teammate 的 lifecycle 綁定 leader process：leader abort 時 teammate 也跟著終止。這雖然直觀，但代表 in-process teammate 不能有長時間背景工作。

### 7.7 AsyncLocalStorage 的 Workload Propagation

使用 `runWithAgentContext()` 捕獲 AsyncLocalStorage context 到 detached closure。這依賴 Node.js/Bun 的 ALS 實現，若有 async gap 沒被正确捕獲，可能導致 analytics/logging 遺漏。

---

## 八、附錄：關鍵檔案索引

| 檔案 | 用途 |
|------|------|
| `src/coordinator/coordinatorMode.ts` | Coordinator 模式核心：feature gate、system prompt、user context |
| `src/tools/AgentTool/AgentTool.tsx` | AgentTool 主實作：async/sync 路由、fork 檢查、MCP 等待 |
| `src/tools/AgentTool/forkSubagent.ts` | Fork sub-agent 專用：fork guard、buildForkedMessages、buildChildMessage |
| `src/tools/AgentTool/runAgent.ts` | Sub-agent 實際執行：tool pool 建構、MCP 初始化、context 建立 |
| `src/tools/AgentTool/agentMemory.ts` | Agent memory 三層 scope（user/project/local）|
| `src/tools/TeamCreateTool/TeamCreateTool.ts` | Team 建立：TeamFile 寫入、成員註冊、task list reset |
| `src/tools/TeamDeleteTool/TeamDeleteTool.ts` | Team 刪除：active 成員檢查、cleanup |
| `src/tools/SendMessageTool/SendMessageTool.ts` | 訊息傳遞：mailbox write、broadcast、shutdown protocol |
| `src/tools/shared/spawnMultiAgent.ts` | Teammate spawn 共享邏輯：tmux/iTerm2 split pane、CLI flag propagation |

---

*本分析報告基於 `win4r/claude-code-2` repo 的洩漏原始碼（2026-03-31），不代表 Anthropic 官方實作。*
