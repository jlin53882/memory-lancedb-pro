# Claude Code CLI Slash Commands 系統深度分析

**分析目標 repo：** https://github.com/win4r/claude-code-2  
**分析日期：** 2026-04-02  
**分析者：** OpenClaw Agent（sub-agent）

---

## 一、Slash Command 系統架構

### 1.1 核心類型系統

Claude Code 的 Command 定義在 `src/types/command.ts`，分為三大類型：

| 類型 | 描述 | 範例 |
|------|------|------|
| `prompt` | 擴充為文字送入模型對話 | `/skills`, `/review` |
| `local` | 純本地執行，回傳 `LocalCommandResult` | `/compact`, `/cost` |
| `local-jsx` | 渲染 Ink（React）UI 對話框 | `/memory`, `/tasks`, `/mcp` |

每個 Command 物件的結構：

```typescript
type Command = CommandBase & (PromptCommand | LocalCommand | LocalJSXCommand)

type CommandBase = {
  name: string
  aliases?: string[]           // 別名（如 /tasks 的別名是 /bashes）
  description: string
  availability?: CommandAvailability[]  // 'claude-ai' | 'console' — 供應商限制
  isEnabled?: () => boolean    // Feature flag / 環境開關
  isHidden?: boolean           // 是否隱藏（不在 typeahead 顯示）
  argumentHint?: string        // 參數提示文字（如 `[enable|disable [server-name]]`）
  immediate?: boolean          // 是否「立即執行」，不等待 stop point（跳過佇列）
  isSensitive?: boolean        // 是否對話歷史中 redact 參數
  loadedFrom?: 'commands_DEPRECATED' | 'skills' | 'plugin' | 'managed' | 'bundled' | 'mcp'
  disableModelInvocation?: boolean  // 是否禁止模型呼叫（技能可被模型呼叫，命令不一定）
  userInvocable?: boolean      // 用戶是否能直接輸入觸發
}
```

### 1.2 命令註冊系統

`src/commands.ts` 是 command 的單一 registry，工廠函式 `COMMANDS()` 回傳所有內建命令：

```typescript
const COMMANDS = memoize((): Command[] => [
  addDir, compact, context, mcp, memory, skills, tasks, ...
  // 動態載入：workflows, proactive, voice, peers, fork 等
  ...(workflowsCmd ? [workflowsCmd] : []),
  ...(process.env.USER_TYPE === 'ant' ? INTERNAL_ONLY_COMMANDS : []),
])
```

**Lazy Loading 模式**：每個 `local` / `local-jsx` 命令的實作都是獨立的 module，透過 `load()` 動態 import：

```typescript
const compact = {
  type: 'local',
  name: 'compact',
  load: () => import('./compact/compact.js'),  // 延遲到第一次呼叫才載入
} satisfies Command
```

**多源合併**（`loadAllCommands`）：

```
1. getSkillDirCommands()     ← ~/.claude/commands/（用戶自訂）
2. getPluginSkills()         ← Plugin 提供的 skills
3. getBundledSkills()        ← 內建 Skills（bundled）
4. getBuiltinPluginSkillCommands() ← 插件內建的 commands
5. getPluginCommands()       ← Plugin 提供的 commands（非 skills）
6. getWorkflowCommands()      ← Workflow script commands
7. COMMANDS()                ← 內建 commands（50+ 個）
```

**過濾與可用性**：

```typescript
export async function getCommands(cwd: string): Promise<Command[]> {
  const all = await loadAllCommands(cwd)
  return all.filter(
    _ => meetsAvailabilityRequirement(_) && isCommandEnabled(_)
  )
}
```

---

## 二、Command 執行環境與權限模型

### 2.1 遠端安全模型（Remote Mode / Bridge）

Claude Code 有完整的「遠端執行」安全模型，分三層：

**REMOTE_SAFE_COMMANDS**：在 `--remote` 模式下，僅這些命令可見（預過濾，防止 race）：

```typescript
export const REMOTE_SAFE_COMMANDS: Set<Command> = new Set([
  session, exit, clear, help, theme, color, vim, cost,
  usage, copy, btw, feedback, plan, keybindings, statusline,
  stickers, mobile,
])
```

**BRIDGE_SAFE_COMMANDS**：允許從 Remote Control bridge（手機/Web 客戶端）安全執行的 `local` 命令：

```typescript
export const BRIDGE_SAFE_COMMANDS: Set<Command> = new Set([
  compact, clear, cost, summary, releaseNotes, files,
])
```

**isBridgeSafeCommand 判定邏輯**：

```typescript
export function isBridgeSafeCommand(cmd: Command): boolean {
  if (cmd.type === 'local-jsx') return false  // Ink UI 無法跨網路render
  if (cmd.type === 'prompt') return true       // prompt 命令純文字，安全
  return BRIDGE_SAFE_COMMANDS.has(cmd)         // local 需要 explicit allowlist
}
```

### 2.2 供應商可用性過濾（Availability）

```typescript
export function meetsAvailabilityRequirement(cmd: Command): boolean {
  if (!cmd.availability) return true
  for (const a of cmd.availability) {
    switch (a) {
      case 'claude-ai':      // claude.ai 訂閱用戶
        if (isClaudeAISubscriber()) return true; break
      case 'console':        // 直接 API key 用戶（api.anthropic.com）
        if (!isClaudeAISubscriber() && !isUsing3PServices() && isFirstPartyAnthropicBaseUrl())
          return true; break
    }
  }
  return false
}
```

### 2.3 技能執行上下文（Fork 模式）

Prompt type 命令（Skills）支援兩種執行模式：

```typescript
type PromptCommand = {
  context?: 'inline' | 'fork'  // inline = 內聯對話；fork = 子 agent
  agent?: string                 // fork 模式使用的 agent 類型（如 'Bash', 'general-purpose'）
  effort?: EffortValue          //  effort 配置
  paths?: string[]               // 應用範圍（當模型接觸特定檔案時才顯示）
}
```

---

## 三、Defer（延後執行）機制

### 3.1 `immediate` 標記——立即執行不等待 Stop Point

```typescript
const mcp = {
  type: 'local-jsx',
  name: 'mcp',
  immediate: true,    // ← 等一行執行，不等 stop point
  argumentHint: '[enable|disable [server-name]]',
  load: () => import('./mcp.js'),
}
```

`immediate: true` 的命令會跳過 normal 佇列，在使用者輸入 `/mcp` 後**立即執行**，不回應模型的 stop point。

### 3.2 Local Command 的 `LocalCommandResult`

```typescript
export type LocalCommandResult =
  | { type: 'text'; value: string }
  | { type: 'compact'; compactionResult: CompactionResult; displayText?: string }
  | { type: 'skip' }  // 跳過訊息，不做任何操作
```

回傳 `type: 'skip'` 可使命令不對模型產生任何干擾。

### 3.3 LocalJSXCommand 的 Callback 機制

```typescript
export type LocalJSXCommandOnDone = (
  result?: string,
  options?: {
    display?: 'skip' | 'system' | 'user'
    shouldQuery?: boolean       // 是否在完成後繼續送訊息給模型
    metaMessages?: string[]     // 額外 meta 訊息
    nextInput?: string          // 帶入下一輪輸入
    submitNextInput?: boolean
  },
) => void

// 實作範例（/mcp）：
export async function call(
  onDone: LocalJSXCommandOnDone,
  _context: unknown,
  args?: string,
): Promise<React.ReactNode> {
  if (args?.startsWith('enable')) {
    return <MCPToggle action="enable" ... />
  }
  return <MCPSettings onComplete={onDone} />
}
```

---

## 四、Compact（上下文壓縮）演算法

### 4.1 雙軌壓縮架構

Claude Code 的 compact 有**兩條路徑**：

```
/compact 呼叫
    │
    ├── trySessionMemoryCompaction()  ← 優先，廉價
    │   若成功 → 直接返回（不走 API）
    │
    ├── REACTIVE_COMPACT 實驗性路徑  ← 透過 reactiveCompact service
    │   若啟用且模式為 reactive-only → 繞道
    │
    └── 傳統 Summarization 路線
        │
        ├── microcompactMessages()   ← 先做輕量預處理（脫圖、脫文件）
        │
        └── compactConversation()     ← 主流程（呼叫 LLM 生成摘要）
```

### 4.2 微壓縮（Microcompact）—— 前處理

```typescript
// 脫圖：圖片 block → [image] 文字標記
// 理由：壓縮 API 呼叫本身可能觸發 prompt-too-long
export function stripImagesFromMessages(messages: Message[]): Message[] {
  return messages.map(message => {
    if (message.type !== 'user' && !Array.isArray(content)) return message
    const newContent = content.flatMap(block => {
      if (block.type === 'image') return [{ type: 'text', text: '[image]' }]
      if (block.type === 'document') return [{ type: 'text', text: '[document]' }]
      // 也處理 tool_result 內嵌的 image
      ...
    })
    return { ...message, message: { ...message.message, content: newContent } }
  })
}

// 脫除無價值的附件（skill_discovery/skill_listing）
// 理由：這些會在 resetSentSkillNames() + discovery signal 中重新浮現，
// 餵給摘要只會浪費 tokens 並產生雜訊
```

### 4.3 摘要生成流程（compactConversation）

**步驟 1：PreCompact Hooks 執行**

```typescript
context.onCompactProgress?.({ type: 'hooks_start', hookType: 'pre_compact' })
context.setSDKStatus?.('compacting')
const hookResult = await executePreCompactHooks({ trigger, customInstructions })
customInstructions = mergeHookInstructions(userInstructions, hookResult.newCustomInstructions)
```

**步驟 2：Prompt Cache 策略**

```typescript
// 實驗確認：第三方 provider 關閉 cache 幾乎必然 cache miss
// 浪費 ~0.76% fleet cache_creation（~38B tok/day）
// 但 3P 環境 GB cache 冷，犧牲可控
const promptCacheSharingEnabled = getFeatureValue_CACHED_MAY_BE_STALE(
  'tengu_compact_cache_prefix',  // Feature gate: 實驗性開關
  true,                          // 預設開（1P），3P 環境後來關閉
)
```

**步驟 3：PTL Retry（Prompt-Too-Long 重試）**

```typescript
// 若 compact 本身收到 PTL error，逐步截斷最舊的 API-round groups
for (;;) {
  summaryResponse = await streamCompactSummary({ messages: messagesToSummarize, ... })
  summary = getAssistantMessageText(summaryResponse)
  if (!summary?.startsWith(PROMPT_TOO_LONG_ERROR_MESSAGE)) break
  
  ptlAttempts++
  const truncated = truncateHeadForPTLRetry(messagesToSummarize, summaryResponse)
  if (!truncated) throw new Error(ERROR_MESSAGE_PROMPT_TOO_LONG)
  messagesToSummarize = truncated
}
```

**步驟 4：Post-Compact 重建**

```
1. context.readFileState.clear()     ← 清除檔案 state cache
2. createPostCompactFileAttachments() ← 重建最多 5 個檔案的 attachment
3. getDeferredToolsDeltaAttachment() ← 重新公告 tools（MCP、agent listing 等）
4. processSessionStartHooks('compact') ← 執行 SessionStart hooks
5. createCompactBoundaryMessage()     ← 插入邊界標記訊息
6. createUserMessage({ isCompactSummary: true }) ← 插入摘要使用者訊息
7. notifyCompaction()                ← 重設 prompt cache read baseline
8. markPostCompaction()               ← 標記已完成壓縮
9. reAppendSessionMetadata()          ← 保留 session 自訂標題/tag
```

### 4.4 Compact Prompt 設計

```typescript
// 嚴格的 no-tools 宣言（放在 prompt 最前面）
const NO_TOOLS_PREAMBLE = `CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.
- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.
- You already have all the context you need in the conversation above.
- Tool calls will be REJECTED and will waste your only turn.`

// 摘要格式要求：<analysis>  scratchpad + <summary>  最終摘要
// analysis 會在 formatCompactSummary() 中剝離，只有 summary 進 context
const DETAILED_ANALYSIS_INSTRUCTION_BASE = `Before providing your final summary,
wrap your analysis in <analysis> tags...`
```

---

## 五、重點命令實作邏輯

### 5.1 `/compact`（本地命令）

**類型**：`local`  
**檔案**：`src/commands/compact/index.ts` + `src/commands/compact/compact.ts`  
**延遲載入**：`load: () => import('./compact.js')`

```typescript
// 入口：call() 函式
export const call: LocalCommandCall = async (args, context) => {
  // 1. 先 try sessionMemoryCompaction（不走 API，廉價）
  const sessionMemoryResult = await trySessionMemoryCompaction(messages, agentId)
  if (sessionMemoryResult) {
    suppressCompactWarning()
    getUserContext.cache.clear?.()
    runPostCompactCleanup()
    return { type: 'compact', compactionResult: sessionMemoryResult, displayText: ... }
  }

  // 2. microcompact（脫圖脫文件）
  const { messages: messagesForCompact } = await microcompactMessages(messages, context)

  // 3. 呼叫 LLM summarization
  const result = await compactConversation(messagesForCompact, context, ..., customInstructions)
  
  return { type: 'compact', compactionResult: result, displayText: ... }
}
```

### 5.2 `/memory`（LocalJSX 命令）

**類型**：`local-jsx`  
**實作**：`src/commands/memory/memory.tsx`（React 组件）

```typescript
export const call: LocalJSXCommandCall = async onDone => {
  clearMemoryFileCaches()
  await getMemoryFiles()
  return <MemoryCommand onDone={onDone} />
}

// MemoryCommand 渲染：
// - Dialog 標題「Memory」
// - MemoryFileSelector 組件（選擇 ~/.claude/memory/ 下的檔案）
// - 支援新建檔案（flag: 'wx'，若已存在則跳過）
// - 使用 $EDITOR / $VISUAL 環境變數開啟編輯器
// - 完成後呼叫 onDone(result)
```

### 5.3 `/skills`（LocalJSX 命令）

**類型**：`local-jsx`  
**實作**：`src/commands/skills/skills.tsx`

```typescript
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: LocalJSXCommandContext,
): Promise<React.ReactNode> {
  return <SkillsMenu onExit={onDone} commands={context.options.commands} />
}
// 渲染 SkillsMenu 組件，接收 commands 清單（getCommands() 回傳的完整列表）
```

### 5.4 `/context`（LocalJSX 命令）

**類型**：`local-jsx`（另有 `contextNonInteractive` 供 non-interactive session）  
**實作**：`src/commands/context/context.tsx`

```typescript
export async function call(onDone, context: LocalJSXCommandContext) {
  const apiView = toApiView(messages)    // 套用與 query.ts 相同的 transform
  if (feature('CONTEXT_COLLAPSE')) {
    view = projectView(view)              // 套用 project view collapse
  }
  const { messages: compactedMessages } = await microcompactMessages(apiView)
  const data = await analyzeContextUsage(
    compactedMessages, mainLoopModel,
    () => appState.toolPermissionContext, tools,
    appState.agentDefinitions, terminalWidth, context,
    undefined,       // mainThreadAgentDefinition
    apiView,         // 原始訊息用於 API usage 萃取
  )
  const output = await renderToAnsiString(<ContextVisualization data={data} />)
  onDone(output)     // 回傳 ANSI string（帶顏色）而不是 React Node
  return null
}
```

**關鍵設計**：套用與正式 API call 相同的 transforms（microcompact、contextCollapse），讓顯示的 token 計數與模型實際看到的相符。

### 5.5 `/tasks`（LocalJSX 命令）

**類型**：`local-jsx`  
**別名**：`/bashes`  
**實作**：`src/commands/tasks/tasks.tsx`

```typescript
export async function call(
  onDone: LocalJSXCommandOnDone,
  context: LocalJSXCommandContext,
): Promise<React.ReactNode> {
  return <BackgroundTasksDialog toolUseContext={context} onDone={onDone} />
}
```

### 5.6 `/mcp`（LocalJSX 命令）

**類型**：`local-jsx`  
**標記**：`immediate: true`（不等待 stop point）  
**實作**：`src/commands/mcp/mcp.tsx`

```typescript
export async function call(onDone, _context, args?: string): Promise<React.ReactNode> {
  if (args) {
    const parts = args.trim().split(/\s+/)
    if (parts[0] === 'no-redirect') return <MCPSettings onComplete={onDone} />
    if (parts[0] === 'reconnect' && parts[1])
      return <MCPReconnect serverName={parts.slice(1).join(' ')} onComplete={onDone} />
    if (parts[0] === 'enable' || parts[0] === 'disable')
      return <MCPToggle action={parts[0]} target={parts[1] ?? 'all'} onComplete={onDone} />
  }
  return <MCPSettings onComplete={onDone} />
}
```

---

## 六、可借鑒的功能設計

### 6.1 多層次 Lazy Loading

```
Command 定義（同步，輕量）
    └── load(): Promise<LocalCommandModule> （第一次執行才 import）
            └── 大型依賴（如 Ink UI、互動式元件）
```

**價值**：節省啟動時間，50+ 命令不需要每個都立即載入完整模組。

### 6.2 Feature Flag 驅動的命令裁剪

```typescript
const proactive = feature('PROACTIVE') || feature('KAIROS')
  ? require('./commands/proactive.js').default : null
const webCmd = feature('CCR_REMOTE_SETUP')
  ? require('./commands/remote-setup/index.js').default : null
```

透過 `feature()` Bun 內建函式在編譯時刪除未啟用的程式碼（Tree Shaking + Dead Code Elimination）。

### 6.3 Remote/Bridge 安全的分層模型

```
遠端客戶端輸入
    ↓
REMOTE_SAFE_COMMANDS（預先過濾，防止 race with CCR init）
    ↓
isBridgeSafeCommand()（精確允許清單）
    ↓
local-jsx → 阻擋（無法跨網路 render Ink）
local     → 檢查 BRIDGE_SAFE_COMMANDS allowlist
prompt    → 允許（純文字擴展，安全）
```

### 6.4 Compact 的 Hook 擴展點

```
PreCompact Hook → 允許外部修改 customInstructions
                  → 可注入額外使用者可見訊息

PostCompact Hook → 執行 session start hooks
                  → 支援壓縮後的特定處理（如通知外部系統）

Hook 指令合併原則：user 指令在前，hook 指令在後（保持 user 意圖優先）
```

### 6.5 雙軌 Compact（廉價 → 昂貴降級）

```
trySessionMemoryCompaction()  ← 記憶體級，不走 API（秒級）
    ↓ 若失敗
compactConversation()         ← LLM API call（代價較高）
    ↓ 若 PTL
truncateHeadForPTLRetry()    ← 截斷最舊 groups，retry（最多 3 次）
```

### 6.6 Prompt Cache 的實驗性 gating

```typescript
const promptCacheSharingEnabled = getFeatureValue_CACHED_MAY_BE_STALE(
  'tengu_compact_cache_prefix',  // GrowthBook feature gate
  true,
)
```

Claude Code 對 compact 的 cache sharing 有完整的 Experiment 機制確認 1P vs 3P 行為差異，並透過 feature gate 可隨時關閉。

---

## 七、與 OpenClaw 現有指令系統的差異

### 7.1 架構模式對比

| 維度 | Claude Code | OpenClaw |
|------|-------------|----------|
| 定義位置 | `src/commands.ts`（單一 registry）| `TOOLS.md` 列 skill，實際分散在各 skill 的 SKILL.md |
| 命令類型 | 3 種（`prompt`/`local`/`local-jsx`）| 目前無類型區分，skill 即代表一組工具集合 |
| 註冊方式 | 靜態陣列 + feature flag 條件展開 | ClawHub 安裝 + `find-skills` 查詢 |
| Lazy Loading | 每個 local 命令独立 `load()` import | 部分 skill 有 lazy 概念，但不普遍 |
| 遠端安全 | 三層 allowlist（REMOTE_SAFE / BRIDGE_SAFE / 精確判斷）| 目前無遠端安全模型 |
| 供應商過濾 | `availability` + `meetsAvailabilityRequirement()`| 無（目前只有單一 model pool） |

### 7.2 Compact 演算法對比

| 維度 | Claude Code | OpenClaw（`memory-compress` skill）|
|------|-------------|-------------------------------------|
| 雙軌設計 | SessionMemoryCompaction（不走 API）| 目前無雙軌 |
| 前處理 | microcompact（strip image/document/attachment）| 目前無前處理 |
| 摘要格式 | `<analysis>` + `<summary>`，analysis 剝離 | 目前無結構化格式要求 |
| PTL Retry | truncateHeadForPTLRetry（逐步截斷）| 目前無 |
| Hook 擴展 | PreCompact + PostCompact hooks | 目前無 hooks 概念 |
| Post-Compact 重建 | 重建 file/tool/agent/MCP attachments | 目前無完整重建邏輯 |
| Cache Baseline 重置 | `notifyCompaction()` + `markPostCompaction()`| 目前無 |

### 7.3 Skill vs Command 命名混淆

Claude Code 的 `/skills` 命名的其實是「命令列表 UI」，而它們的「技能」概念由 `type: 'prompt'` commands 代表（可被模型呼叫）。  
OpenClaw 的 `skills/` 資料夾則是獨立的技能系統，命名上有差異但概念上相對一致（都是提供能力的封裝）。

### 7.4 Immediate 機制

Claude Code 的 `immediate: true` 允許命令不打斷模型 flow 直接執行。OpenClaw 目前無此機制，所有操作都會經過模型處理流程。

---

## 八、總結與建議

### OpenClaw 可借鑒的優先順序

1. **高價值**：Compact 前處理（strip image/document）—— 避免 summary API call 本身 PTL
2. **高價值**：Compact 的 `<analysis>` + `<summary>` 結構化格式——提升摘要品質
3. **高價值**：雙軌 Compact（SessionMemory → LLM 降級）—— 節省 API 成本
4. **中價值**：Feature flag 驅動的命令裁剪——減少無用程式碼負載
5. **中價值**：Remote/Bridge 安全分層——為未來多客戶端支援奠基
6. **中價值**：Hook 擴展點（PreCompact/PostCompact）——讓外部系統可以干預壓縮流程
7. **低價值**：GrowthBook feature gate 整合——需要基礎設施支援

### 現有落差

- OpenClaw 目前沒有 `local` / `local-jsx` / `prompt` 的命令類型區分
- OpenClaw 的 Compact（`memory-compress`）尚無 PTL retry / microcompact / hook 機制
- OpenClaw 尚無遠端安全模型（但目前場景不需要）
- Claude Code 的 `load()` lazy loading 模式值得 OpenClaw 的 skill 系統參考
