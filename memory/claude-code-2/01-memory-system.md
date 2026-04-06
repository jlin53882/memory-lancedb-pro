# Claude Code CLI 記憶系統深度分析報告

**分析目標 repo：** https://github.com/win4r/claude-code-2  
**分析日期：** 2026-04-02  
**分析範圍：** `src/memdir/`、`src/services/extractMemories/`、`src/services/teamMemorySync/`

---

## 一、`src/memdir/` — 持久化記憶目錄實作

### 1.1 核心資料結構

Claude Code 的記憶系統採用**磁碟檔案樹**結構，組織如下：

```
~/.claude/
└── projects/
    └── <sanitized-git-root>/
        └── memory/
            ├── MEMORY.md          ← 入口索引檔（被載入 system prompt）
            ├── user_role.md       ← 各類型記憶檔案（frontmatter + 內容）
            ├── feedback_testing.md
            ├── project_deadline.md
            └── reference_linear.md
            └── team/              ← 團隊記憶子目錄（可選）
                ├── MEMORY.md
                └── ...
            └── logs/              ← KAIROS 每日日誌模式
                └── YYYY/MM/YYYY-MM-DD.md
```

**路徑解析優先順序（`paths.ts`）：**

| 優先順序 | 來源 | 說明 |
|----------|------|------|
| 1 | `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` env | Cowork SDK 全域覆寫 |
| 2 | `settings.json` 的 `autoMemoryDirectory` | 使用者信任的設定來源 |
| 3 | `~/.claude/projects/<sanitized-git-root>/memory/` | 預設路徑，按 git root 分組 |

**安全驗證（`teamMemPaths.ts`）：**

- 路徑必須為絕對路徑（排除 `../foo` 之相對路徑）
- 拒絕 Windows drive root（如 `C:`）、UNC 路徑（`\\server\share`）
- 防止 null byte 截斷攻擊
- **寫入時**額外做 symlink escape 檢測：`realpathDeepestExisting()` 解析最深存在祖先目錄，對比 canonical 路徑是否仍在團隊記憶目錄內

**記憶內容的 frontmatter 格式（`memoryTypes.ts`）：**

```markdown
---
name: {{memory name}}
description: {{one-line description — 用於判斷相關性}}
type: {{user, feedback, project, reference}}
---

{{memory content}}
```

### 1.2 記憶分類學（Four-Type Taxonomy）

四種封閉類型（`memoryTypes.ts`）：

| 類型 | 描述 | 何時儲存 | 主體結構 |
|------|------|----------|----------|
| `user` | 使用者角色、目標、知識背景 | 學習到任何使用者細節時 | 直接描述 |
| `feedback` | 對 agent 行為的糾正或確認 | 任何「不要這樣做」或「很好，繼續」時 | **Rule + Why + How to apply** |
| `project` | 專案範圍、截止日期、決策動機 | 學習到誰在做什麼、為什麼、何時 | **Fact + Why + How to apply** |
| `reference` | 外部系統的指標（如 Linear、Grafana） | 學習到外部資源位置時 | 指標描述 |

**明確排除的內容：**
- 程式碼 patterns、架構、git history（可從當前專案狀態推導）
- 已經存在於 CLAUDE.md 的內容
- 臨時任務狀態、Ephemeral 上下文

**「忽略」語義（`WHEN_TO_ACCESS_SECTION`）：**
> 使用者說「*ignore* memory about X」→ 完全視同 MEMORY.md 空白，不引用、不應用、不提及。

### 1.3 入口檔（MEMORY.md）管理

- `MEMORY.md` 本身**不是記憶**，而是 index index
- 每行格式：`- [Title](file.md) — one-line hook`，需控制在 ~150 字以內
- 行數上限 200 行；超過會截斷並附加警告
- 單一檔案上限 25,000 bytes（防範長行 index entry）

### 1.4 `findRelevantMemories` — 主動召回

觸發時機：當查詢涉及「過去上下文」時。

流程（`findRelevantMemories.ts`）：

```
1. scanMemoryFiles() — 讀取所有 .md 的 frontmatter（description + type），最新優先
2. 過濾掉本輪已顯示過的檔案（避免重複）
3. 交給 Sonnet 模型做 relevance selection（最多 5 個）
4. 返回 { path, mtimeMs } 列表
```

**查詢時年齡戳記（`memoryAge.ts`）：**

```typescript
function memoryAge(mtimeMs: number): string {
  // "today" | "yesterday" | "47 days ago"
}
```

對 1 天以上的記憶自動附加 staleness 警告：
> 「This memory is X days old. Memories are point-in-time observations... Verify against current code before asserting as fact.」

---

## 二、`src/services/extractMemories/` — 自動記憶萃取系統

### 2.1 萃取觸發時機

在每個**完整查詢循環結束時**（model 產生最終回應、無 tool calls），透過 `handleStopHooks` 觸發。

採用 **forked agent 模式**（`runForkedAgent`）——完美複製主對話的 prompt cache，獨立在背景執行。

### 2.2 萃取流程

```
handleStopHooks
  → executeExtractMemories()
    → runExtraction()
      
      1. 檢查 hasMemoryWritesSince() — 主 agent 是否有寫入記憶？
         → 若有：跳過萃取，直接前進 cursor
      
      2. scanMemoryFiles() — 預先注入現有記憶 manifest（省一個 turn）
      
      3. runForkedAgent({
           promptMessages: [buildExtractPrompt()],
           maxTurns: 5,         // 防止 rabbit-hole
           canUseTool: createAutoMemCanUseTool(),
           skipTranscript: true  // 不寫入 transcript
         })
      
      4. extractWrittenPaths() — 取出寫入的檔案路徑
      
      5. appendSystemMessage(MemorySavedMessage) — 通知主 agent
```

### 2.3 萃取 Prompt 設計

**雙版本：**
- `buildExtractAutoOnlyPrompt()` — 單一目錄，無 scope 標籤
- `buildExtractCombinedPrompt()` — auto + team 雙目錄，每個 type 有 `<scope>always private</scope>` 或 `<scope>default to private</scope>` 指引

**關鍵指令：**
```
You MUST only use content from the last ~N messages to update your persistent memories.
Do not waste any turns attempting to investigate or verify that content further —
no grepping source files, no reading code to confirm a pattern exists, no git commands.
```

萃取 agent 被嚴格限制為**純推理**：只能讀取對話歷史，不能去讀 source code 或執行 git 來「確認」記憶的正確性。

### 2.4 Throttle 機制

透過 GrowthBook feature flag `tengu_bramble_lintel` 控制：

```
turnsSinceLastExtraction++ 
if (turnsSinceLastExtraction < N) return  // 跳過
```

Trailing runs（停滯後的額外萃取）不受此限制。

### 2.5 互斥機制

當主 agent 自己寫入了記憶，萃取 agent 會跳過（`hasMemoryWritesSince`）並前進 cursor。這讓兩者互斥——每次 turn 只會有一方實際萃取。

---

## 三、`src/services/teamMemorySync/` — 團隊記憶同步

### 3.1 同步架構

**API 契約（基於 GitHub repo scope）：**

```
GET  /api/claude_code/team_memory?repo={owner/repo}
     → TeamMemoryData { organizationId, repo, version, checksum, content: { entries, entryChecksums } }

PUT  /api/claude_code/team_memory?repo={owner/repo}
     → upsert semantics（不在 PUT 中的 key 會被保留）
```

**Sync 狀態（`SyncState`）：**

```typescript
type SyncState = {
  lastKnownChecksum: string | null   // ETag for 304/not-modified
  serverChecksums: Map<string, string>  // sha256:<hex> per key
  serverMaxEntries: number | null     // 從 413 error 動態學習
}
```

### 3.2 Pull / Push 語意

| 方向 | 語意 | 衝突策略 |
|------|------|----------|
| **Pull** | 伺服器覆寫本地檔案 | server wins per-key |
| **Push** | Delta 上傳（只上 hash 不同的 key） | 412 Conflict → probe `?view=hashes` → retry |

**Pull 流程：**
```
1. GET with If-None-Match (ETag)
2. 若 304 → 直接返回（無變動）
3. 若 200 → 解析 TeamMemoryDataSchema
4. 寫入 local 檔案（skip 如果磁碟內容已相同，保留 mtime）
5. 更新 serverChecksums
```

**Push 流程：**
```
1. readLocalTeamMemory() — 讀取所有本地檔案（secret scan 在此階段）
2. localHashes = sha256(local content) per file
3. Delta = { key: content | localHash != serverChecksums[key] }
4. 若 Delta 為空 → 完成
5. batchDeltaByBytes() — 切成 ≤200KB 的批次（防止 gateway 413）
6. PUT 每個批次（with If-Match ETag）
7. 若 412 → fetchTeamMemoryHashes() → 刷新 serverChecksums → 重算 Delta → retry
8. MAX_CONFLICT_RETRIES = 2
```

### 3.3 安全性：Secret Scanner

**在寫入磁碟前（Pull 路徑）和上傳前（Push 路徑）都會掃描。**

採用 gitleaks 規則子集（高置信度前綴），只記錄 rule ID 和標籤，**絕不**記錄或上傳 secret 本身。

目前規則涵蓋：
- 雲端：AWS、GCP、Azure、DigitalOcean
- AI APIs：Anthropic（含動態組裝前綴防 bundle 分析）、OpenAI、HuggingFace
- VCS：GitHub PAT/fine-grainedPAT/oauth/refresh、GitLab PAT/deploy token
- 通訊：Slack (bot/user/app token)、Twilio、SendGrid
- 開發工具：NPM、PyPI、Databricks、HashiCorp TF、Pulumi、Postman
- 可觀測性：Grafana (api-key/cloud/service-account)、Sentry (user/org token)
- 支付：Stripe、Shopify
- **Private Key**（完整 PEM 格式）

### 3.4 Watcher 架構

使用 Node.js `fs.watch({ recursive: true })`（非 chokidar），避免 Bun + chokidar 4 在 macOS 上使用 FSEvents 而非 fsevents 的 fd leak 問題。

**Debounce：** 2000ms，確保短時間內多次寫入只觸發一次 push。

**Push suppression：** 遇到 permanent failure（`no_oauth`、4xx 非 409/429）後，停止 retry 直到：
- 檔案被刪除（`unlink` 事件清除 suppression）
- Session 重啟

---

## 四、可借鑒的設計模式

### 4.1 雙軌萃取（主動寫入 vs 自動萃取）

```
主 agent 主動寫入 → 萃取 agent 跳過（互斥）
主 agent 未寫入   → 萃取 agent 在 turn 結束時自動補足
```

**對 OpenClaw 的價值：** 現有 OpenClaw 依賴使用者明確觸發 `/remember`，此模式可實現「背景自動萃取 + 即時主動寫入」的互補。

### 4.2 記憶 mtime 驅動的 Freshness 警告

```typescript
memoryFreshnessNote(mtimeMs) 
// → 1天以上自動附加 "<system-reminder> X days old... </system-reminder>"
```

**對 OpenClaw 的價值：** 可直接移植到 OpenClaw 的 `memory_recall` 回傳結果，依據 `ingested_at` 時間自動附加 staleness 警告。

### 4.3 萃取 agent 的嚴格工具限制

```typescript
createAutoMemCanUseTool(): CanUseToolFn
// → 允許：Read/Grep/Glob/read-only Bash
// → 禁止：MCP、AgentTool、網路呼叫
// → 限制：Edit/Write 只能在 auto-mem 目錄內
```

**對 OpenClaw 的價值：** 萃取 subagent 應只讀取對話歷史，不去讀 source code——這是防止萃取 agent「確認」錯誤記憶的關鍵。

### 4.4 四型 taxonomy 的「What NOT to save」黑名單

明確定義「可推導內容排除」規則，並透過 eval 驗證：
- 記憶名稱具體函式/檔案 → 使用前需 verify
- Snapshot 類記憶 → 預設用 `git log` / 讀 code 取代

**對 OpenClaw 的價值：** 當前 OpenClaw 的 LanceDB 召回沒有這層「記憶邊界」教育，可能導致 agent 拿 stale code-state 記憶當事實。

### 4.5 Secret Scanner 的 gitleaks 規則子集

在團隊同步前/後各掃一次，確保 secret：
1. 不會被上傳到共享 server
2. 不會被寫入團隊成員的 local 檔案

### 4.6 路徑安全的兩階段驗證

```typescript
// Stage 1: string-level containment check
resolve(path).startsWith(teamDir)  

// Stage 2: symlink escape check  
realpathDeepestExisting(resolvedPath) → compare with realpath(teamDir)
```

### 4.7 SyncState 的 closure-scoped 管理

所有 mutable state（ETag、checksum map、suppression flag）封裝在 `createSyncState()` 回傳的物件中，由 caller 持有和 threading，避免 module-level 全域狀態。

---

## 五、潛在風險或問題

### 5.1 萃取延遲

萃取 agent 在查詢結束後才執行，若使用者在萃取完成前結束 session，可能漏掉本次萃取的記憶。雖然有 `drainPendingExtraction()` 在 shutdown 時等待，但仍可能在 2s grace period 內被 kill。

### 5.2 Push suppression 的永久阻斷

一旦觸發 `no_oauth` 或 4xx permanent failure，團隊 sync 會完全停止直到 session restart 或團隊記憶檔案被刪除。如果原因是網路問題（非 auth），使用者不會收到任何通知。

### 5.3 Delta 上傳的批次失敗

當 Delta 很大、被切成多個批次時，前幾個批次成功、最後一個失敗是可能發生的。這時部分 key 已 commit、部分未 commit，下次 push 會重新上傳所有 dirty key（因為 serverChecksums 已更新）。**沒有自動修復機制。**

### 5.4 「忽略」語義的實作範圍

`WHEN_TO_ACCESS_SECTION` 說「*ignore* memory → proceed as if MEMORY.md were empty」，但這只對**主動召回**有意義。若模型在 system prompt 已經將 MEMORY.md 載入為背景資訊，「忽略」仍會摻入回應——目前沒有機制確保忽略真的完全生效。

### 5.5 KAIROS 每日日誌模式的蒸餾依賴

`/dream` skill（夜間蒸餾）若漏跑，累積的 logs 無法自動轉換成 `MEMORY.md`。這是單點故障依賴。

### 5.6 `serverChecksums` 的 283027 向後相容

若 server 部署落後（無 `?view=hashes` 端點），412 conflict 發生時 probe 會失敗，整個 push 就失敗。沒有 graceful degradation 機制。

---

## 六、總結：與 OpenClaw 的對照

| 面向 | Claude Code | OpenClaw 現況 |
|------|------------|---------------|
| 儲存媒介 | 磁碟檔案樹（`.md`） | LanceDB（向量）+ `MEMORY.md` |
| 觸發方式 | 主動寫入 + 自動萃取（背景 fork） | 主要依賴 `/remember`、少數 cron |
| 召回方式 | frontmatter scan → LLM 選擇（top-5 relevance） | `memory_recall` 向量相似度檢索 |
| 記憶生命週期 | mtime 追蹤 + 明確 freshness 警告 | `ingested_at` 有 TTL，但無自動警告 |
| 團隊共享 | 雙目錄（private/team）+ 同步 server | 無 |
| Secret 保護 | gitleaks scan on read+write | 無 |
| 萃取的嚴格限制 | 不准讀 source、不准 git verify | 不適用（萃取機制不同）|

---

*報告生成：subagent 分析 | 2026-04-02*
