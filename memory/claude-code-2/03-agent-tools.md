# Claude Code CLI Agent Tools 實作深度分析

> 分析目標 repo：https://github.com/win4r/claude-code-2
> 分析日期：2026-04-02

---

## 一、工具系統架構總覽

### 1.1 核心類型定義（Tool.ts）

Claude Code 的工具系統建立在一個強大的 `Tool` 泛型介面上：

```typescript
type Tool<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // 核心方法
  call(args, context, canUseTool, parentMessage, onProgress): Promise<ToolResult<Output>>
  description(input): Promise<string>
  
  // Schema 定義
  readonly inputSchema: Input
  readonly inputJSONSchema?: ToolInputJSONSchema
  readonly outputSchema?: z.ZodType<unknown>
  
  // 權限與驗證
  validateInput?(input, context): Promise<ValidationResult>
  checkPermissions(input, context): Promise<PermissionResult>
  preparePermissionMatcher?(input): Promise<(pattern: string) => boolean>
  
  // 行為斷言
  isConcurrencySafe(input): boolean
  isReadOnly(input): boolean
  isDestructive?(input): boolean
  isSearchOrReadCommand?(input): { isSearch, isRead, isList }
  isOpenWorld?(input): boolean
  
  // 呈現與渲染
  renderToolResultMessage(content, progress, options): React.ReactNode
  renderToolUseMessage(input, options): React.ReactNode
  mapToolResultToToolResultBlockParam(content, toolUseID): ToolResultBlockParam
  
  // 中介層鉤子
  backfillObservableInput?(input): void
  
  // 元數據
  readonly name: string
  readonly maxResultSizeChars: number
  readonly shouldDefer?: boolean
  readonly alwaysLoad?: boolean
}
```

**關鍵設計模式：**
- `buildTool()` 工廠函數：自動填入預設值（fail-closed 原則）
- `lazySchema()`：延遲 schema 解析，支援條件性功能開關
- 支援 Zod 與 JSON Schema 雙格式輸入

### 1.2 工具註冊系統（tools.ts）

```typescript
// 工具清單組装
export function getTools(permissionContext: ToolPermissionContext): Tools {
  // Simple 模式：僅 Bash/Read/Edit
  if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
    return filterToolsByDenyRules(simpleTools, permissionContext)
  }
  
  // 完整模式：取得所有基礎工具
  const tools = getAllBaseTools()
  let allowedTools = filterToolsByDenyRules(tools, permissionContext)
  
  // REPL 模式下隱藏原始工具
  if (isReplModeEnabled()) {
    allowedTools = allowedTools.filter(tool => !REPL_ONLY_TOOLS.has(tool.name))
  }
  
  return allowedTools.filter((_, i) => _.isEnabled())
}

// MCP 工具整合
export function assembleToolPool(
  permissionContext: ToolPermissionContext,
  mcpTools: Tools,
): Tools {
  const builtInTools = getTools(permissionContext)
  const allowedMcpTools = filterToolsByDenyRules(mcpTools, permissionContext)
  
  // 按名稱排序以確保 prompt 快取穩定性
  // built-in 工具維持連續前缀，MCP 工具排在後面
  return uniqBy(
    [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
    'name',
  )
}
```

**特色：**
- **條件性載入**：透過 `feature()` 閘道實現 dead code elimination
- **權限過濾**：按 deny rules 預先過濾工具
- **Prompt 快取穩定**：工具排序固定，確保 API prompt 快取命中

---

## 二、代表性工具實作邏輯

### 2.1 BashTool — 安全性與靈活性典範

**Input Schema：**
```typescript
const inputSchema = lazySchema(() => z.strictObject({
  command: z.string().describe('The command to execute'),
  timeout: semanticNumber(z.number().optional()).describe(`...`),
  description: z.string().optional().describe('...'),
  run_in_background: semanticBoolean(z.boolean().optional()),
  dangerouslyDisableSandbox: semanticBoolean(z.boolean().optional()),
  _simulatedSedEdit: z.object({...}).optional() // 内部使用
}))
```

**權限模型（bashPermissions.ts — 20KB+）：**
```typescript
async checkPermissions(input, context): Promise<PermissionResult> {
  return bashToolHasPermission(input, context)
}
```

**實現亮點：**

1. **命令語意分類**
```typescript
// 自動判斷是否為 read-only/search 命令
isSearchOrReadCommand(input) {
  const parsed = splitCommandWithOperators(input.command)
  // 搜索命令：find, grep, rg, ag, ack, locate, which
  // 讀取命令：cat, head, tail, less, more, wc, stat
  // 目錄列表：ls, tree, du
}
```

2. **安全驗證層**
```typescript
async validateInput(input: BashToolInput): Promise<ValidationResult> {
  // 阻止長時間 sleep（應使用 Monitor tool）
  if (detectBlockedSleepPattern(input.command)) {
    return { result: false, message: '...', errorCode: 10 }
  }
  return { result: true }
}
```

3. **Sandbox 隔離**
```typescript
shouldUseSandbox(command) // 根據命令類型決定是否啟用沙盒
```

4. **自動背景化**
```typescript
// 超過 15 秒的阻塞命令自動背景執行
const ASSISTANT_BLOCKING_BUDGET_MS = 15_000
```

### 2.2 FileReadTool — 智慧內容處理

**Input Schema：**
```typescript
z.strictObject({
  file_path: z.string().describe('The absolute path to the file to read'),
  offset: semanticNumber(z.number().int().nonnegative().optional()),
  limit: semanticNumber(z.number().int().positive().optional()),
  pages: z.string().optional().describe('Page range for PDF files')
})
```

**Output Schema（ discriminated union）：**
```typescript
z.discriminatedUnion('type', [
  z.object({ type: 'text', file: {...} }),
  z.object({ type: 'image', file: { base64, type, dimensions } }),
  z.object({ type: 'notebook', file: { cells } }),
  z.object({ type: 'pdf', file: { base64 } }),
  z.object({ type: 'file_unchanged', file: { filePath } }) // 重複讀取優化
])
```

**實現亮點：**

1. **內容去重（Deduplication）**
```typescript
// 若讀取的範圍與之前相同且檔案未變更，回傳 stub
const existingState = readFileState.get(fullFilePath)
if (rangeMatch && mtimeMs === existingState.timestamp) {
  return { data: { type: 'file_unchanged', file: { filePath } } }
}
```

2. **多格式原生支援**
- 圖片：自動壓縮、調整大小、控制 token 預算
- PDF：分頁提取、content block 傳遞
- Notebook：cell 解析與渲染

3. **Security Hooks 整合**
```typescript
backfillObservableInput(input) {
  input.file_path = expandPath(input.file_path) // 展開 ~ 路徑
}
preparePermissionMatcher({ file_path }) {
  return pattern => matchWildcardPattern(pattern, file_path)
}
```

### 2.3 FileEditTool — 安全的檔案修改

**Input Schema：**
```typescript
z.strictObject({
  file_path: z.string(),
  old_string: z.string(),
  new_string: z.string(),
  replace_all: z.boolean().optional()
})
```

**驗證流程（validateInput）：**

1. **權限檢查**：matchingRuleForInput() 檢查 deny rules
2. **檔案大小限制**：MAX_EDIT_FILE_SIZE = 1GB
3. **存在性檢查**：檔案不存在時的處理
4. **變更檢測**：確認檔案自 read 以來未被修改
5. **字串匹配**：使用 findActualString() 處理引號正規化
6. **多重匹配警告**：replace_all=false 時若有多處匹配則報錯
7. **Settings 檔案驗證**：特殊處理 CLAUDE.md 等設定檔

**實現亮點：**
```typescript
// 原子性讀-修改-寫入
const { content: originalFileContents } = readFileForEdit(absoluteFilePath)
// ... 生成 patch
writeTextContent(absoluteFilePath, updatedFile, encoding, endings)
// 更新 readFileState timestamp
```

### 2.4 GlobTool / GrepTool — 搜尋工具

**Glob Input：**
```typescript
z.strictObject({
  pattern: z.string().describe('The glob pattern'),
  path: z.string().optional().describe('Directory to search in')
})
```

**權限模型：** 使用 checkReadPermissionForTool() 整合檔案系統權限

**結果限制：** maxResults 預設 100，自動標記 truncated

### 2.5 WebFetchTool — 網頁擷取

**特色：**
- `shouldDefer: true` — 需透過 ToolSearch 啟用
- 基於 hostname 的權限規則
- 預批准主機白名單（preapproved.ts）
- 內容長度限制（MAX_MARKDOWN_LENGTH）

```typescript
async checkPermissions(input, context): Promise<PermissionDecision> {
  // 檢查預批准主機
  if (isPreapprovedHost(parsedUrl.hostname)) {
    return { behavior: 'allow', ... }
  }
  // 檢查規則：domain:hostname
  const ruleContent = `domain:${hostname}`
  // ...
}
```

### 2.6 WebSearchTool — Web Search 整合

**特色：**
- 實際使用 API 的 web_search tool（Beta）
- 最多 8 次搜尋（max_uses: 8）
- 支援 allowed_domains / blocked_domains
- 進度追蹤：query_update、search_results_received

```typescript
async call(input, context, _canUseTool, _parentMessage, onProgress) {
  // 使用 queryModelWithStreaming 進行模型調用
  const queryStream = queryModelWithStreaming({
    // ...
    tools: [],
    extraToolSchemas: [makeToolSchema(input)]
  })
}
```

### 2.7 AgentTool — 子代理管理

**Input Schema：**
```typescript
z.object({
  description: z.string(),      // 3-5 字短描述
  prompt: z.string(),           // 代理任務
  subagent_type: z.string().optional(),
  model: z.enum(['sonnet', 'opus', 'haiku']).optional(),
  run_in_background: z.boolean().optional(),
  // KAIROS 功能
  name: z.string().optional(),           // 代理名稱（可定址）
  team_name: z.string().optional(),
  mode: permissionModeSchema().optional(),
  isolation: z.enum(['worktree', 'remote']).optional(),
  cwd: z.string().optional()
})
```

**實現亮點：**

1. **多種執行模式**
   - 同步完成（status: 'completed'）
   - 非同步啟動（status: 'async_launched'）
   - 團隊成員（status: 'teammate_spawned'）
   - 遠端啟動（status: 'remote_launched'）

2. **隔離模式**
   - worktree：建立 git worktree 隔離副本
   - remote：遠端 CCR 環境執行

3. **Progress 追蹤**
```typescript
createProgressTracker(), emitTaskProgress(), getProgressUpdate()
```

### 2.8 MCPTool — MCP 協議橋接

**特色：**
- 通用 passthrough 工具（input 為 passthrough）
- 動態名稱覆寫（mcpClient.ts 設定）
- 結果截斷處理

```typescript
export const MCPTool = buildTool({
  isMcp: true,
  isOpenWorld() { return false }, // 覆寫
  name: 'mcp', // 覆寫
  async checkPermissions(): Promise<PermissionResult> {
    return { behavior: 'passthrough', message: 'MCPTool requires permission.' }
  }
})
```

### 2.9 LSPTool — 語言伺服器整合

**Input Schema：**
```typescript
z.strictObject({
  operation: z.enum([
    'goToDefinition', 'findReferences', 'hover',
    'documentSymbol', 'workspaceSymbol', 'goToImplementation',
    'prepareCallHierarchy', 'incomingCalls', 'outgoingCalls'
  ]),
  filePath: z.string(),
  line: z.number().int().positive(),
  character: z.number().int().positive()
})
```

**特色：**
- `shouldDefer: true` — 延遲載入
- `isEnabled()` — 檢查 LSP 連接狀態
- 輸出格式化（formatters.ts）
- 檔案大小限制：MAX_LSP_FILE_SIZE_BYTES = 10MB

---

## 三、Tool Call Loop 機制

### 3.1 執行流程（toolExecution.ts）

```typescript
export async function* runToolUse(
  toolUse: ToolUseBlock,
  assistantMessage: AssistantMessage,
  canUseTool: CanUseToolFn,
  toolUseContext: ToolUseContext,
): AsyncGenerator<MessageUpdateLazy, void> {
  
  // 1. 工具查找
  let tool = findToolByName(tools, toolName)
  
  // 2. 驗證輸入（validateInput）
  const validation = await tool.validateInput?.(input, context)
  if (!validation.result) {
    yield createToolResultError(validation.message)
    return
  }
  
  // 3. 權限檢查（checkPermissions）
  const permission = await tool.checkPermissions(input, context)
  if (permission.behavior === 'deny') {
    yield createToolResultDenied(permission.message)
    return
  }
  
  // 4. Pre-Tool-Use Hooks
  await runPreToolUseHooks(tool, input, context)
  
  // 5. 執行工具（tool.call）
  const result = await tool.call(input, context, canUseTool, parentMessage, onProgress)
  
  // 6. Post-Tool-Use Hooks
  await runPostToolUseHooks(tool, result, context)
  
  // 7. 產生結果訊息
  const blockParam = tool.mapToolResultToToolResultBlockParam(result.data, toolUse.id)
  yield { message: createUserMessage({ content: [blockParam] }) }
}
```

### 3.2 Hook 系統（toolHooks.ts）

```typescript
// Pre-Tool-Use Hooks
async function runPreToolUseHooks(tool, input, context) {
  for (const hook of preToolUseHooks) {
    const decision = await hook({ tool, input, context })
    if (decision === 'deny') throw new HookDeniedError()
  }
}

// Post-Tool-Use Hooks
async function runPostToolUseHooks(tool, result, context) {
  for (const hook of postToolUseHooks) {
    await hook({ tool, result, context })
  }
}
```

### 3.3 錯誤處理與重試

```typescript
// 錯誤分類
function classifyToolError(error: unknown): string {
  if (error instanceof TelemetrySafeError) return error.telemetryMessage
  if (error instanceof Error) {
    const errnoCode = getErrnoCode(error)
    if (errnoCode) return `Error:${errnoCode}`
    return error.name
  }
  return 'UnknownError'
}

// 重試邏輯（withRetry.ts）
async function withRetry(fn, options) {
  const { maxRetries, backoffMs } = options
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxRetries || !isRetryable(error)) throw error
      await sleep(backoffMs * Math.pow(2, attempt))
    }
  }
}
```

---

## 四、權限系統架構

### 4.1 PermissionContext 結構

```typescript
type ToolPermissionContext = {
  mode: PermissionMode           // 'default' | 'plan' | 'auto' | 'bypass'
  additionalWorkingDirectories: Map<string, AdditionalWorkingDirectory>
  alwaysAllowRules: ToolPermissionRulesBySource
  alwaysDenyRules: ToolPermissionRulesBySource
  alwaysAskRules: ToolPermissionRulesBySource
  isBypassPermissionsModeAvailable: boolean
  shouldAvoidPermissionPrompts?: boolean
  awaitAutomatedChecksBeforeDialog?: boolean
}
```

### 4.2 規則匹配

```typescript
// Shell 命令匹配（bashPermissions.ts）
async preparePermissionMatcher({ command }) {
  const parsed = await parseForSecurity(command)
  const subcommands = parsed.commands.map(c => c.argv.join(' '))
  return pattern => subcommands.some(cmd => matchWildcardPattern(pattern, cmd))
}

// 檔案路徑匹配（filesystem.ts）
async preparePermissionMatcher({ file_path }) {
  return pattern => matchWildcardPattern(pattern, file_path)
}
```

### 4.3 權限決策流程

```typescript
async checkPermissions(input, context): Promise<PermissionResult> {
  // 1. 檢查 alwaysDenyRules
  const denyRule = matchingRuleForInput(path, context, 'deny')
  if (denyRule) return { behavior: 'deny', decisionReason: { type: 'rule', rule: denyRule } }
  
  // 2. 檢查 alwaysAllowRules
  const allowRule = matchingRuleForInput(path, context, 'allow')
  if (allowRule) return { behavior: 'allow', decisionReason: { type: 'rule', rule: allowRule } }
  
  // 3. 詢問使用者
  return { behavior: 'ask', message: '...' }
}
```

---

## 五、可借鑒的設計模式

### 5.1 buildTool 工廠模式

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: () => false,
  isReadOnly: () => false,
  isDestructive: () => false,
  checkPermissions: (input) => Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: () => '',
  userFacingName: () => '',
}

export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
  return { ...TOOL_DEFAULTS, userFacingName: () => def.name, ...def }
}
```

**優點：** 減少樣板程式碼，統一預設行為

### 5.2 lazySchema 延遲解析

```typescript
export const lazySchema = <T>(factory: () => T): (() => T) => {
  let cache: T | null = null
  return () => {
    if (cache === null) cache = factory()
    return cache
  }
}
```

**優點：** 支援條件性功能閘道，延遲昂貴的 Zod 解析

### 5.3 分層驗證架構

1. **Input Validation**（validateInput）：語法與語意檢查
2. **Permission Check**（checkPermissions）：權限與安全規則
3. **Pre-Tool Hooks**：自動化安全檢查（classifier、hooks）
4. **Post-Tool Hooks**：日誌、通知、分析

### 5.4 Tool Result 持久化

```typescript
// 超過閾值自動持久化到磁碟
maxResultSizeChars: 30_000 // BashTool
maxResultSizeChars: 100_000 // WebFetchTool

if (output.length > maxResultSizeChars) {
  const path = await persistToFile(output)
  return { data: { persistedOutputPath: path, ... } }
}
```

### 5.5 去重與快取機制

```typescript
// FileReadTool 去重
readFileState.get(fullFilePath) // LRU cache
if (mtimeMs === existingState.timestamp && rangeMatch) {
  return { type: 'file_unchanged' }
}
```

---

## 六、OpenClaw 可借鑒的功能

### 6.1 優先實作

| 功能 | 來源 | 說明 |
|------|------|------|
| **buildTool 工廠** | Tool.ts | 統一工具創建流程，減少樣板程式碼 |
| **lazySchema 延遲載入** | utils/lazySchema.ts | 支援條件性工具開關 |
| **分層驗證** | 各工具 validateInput + checkPermissions | 語法檢查 → 權限檢查 → Hooks |
| **maxResultSizeChars** | 各工具定義 | 結果自動持久化，避免 context 膨脹 |
| **isConcurrencySafe** | Tool.ts | 並發安全宣告，支援平行執行 |
| **preparePermissionMatcher** | BashTool/FileReadTool | 細粒度鉤子匹配 |

### 6.2 中期規劃

| 功能 | 來源 | 說明 |
|------|------|------|
| **Tool Search 延遲載入** | WebFetchTool.shouldDefer | 工具過多時延遲載入，需主動搜索 |
| **Shell 命令語意分類** | BashTool.isSearchOrReadCommand | 自動識別 read-only/search 命令 |
| **Sandbox 隔離** | BashTool/shouldUseSandbox | 命令級沙盒控制 |
| **自動背景化** | BashTool.ASSISTANT_BLOCKING_BUDGET_MS | 長任務自動 background |
| **MCP 整合** | MCPTool + mcpClient.ts | 標準化 MCP 工具橋接 |

### 6.3 長期願景

| 功能 | 來源 | 說明 |
|------|------|------|
| **Agent Tool 子代理** | AgentTool.tsx | 任務分解與委派 |
| **多代理團隊** | AgentTool (KAIROS) | 命名代理、團隊協作 |
| **隔離模式** | AgentTool.isolation: worktree | git worktree 隔離 |
| **Progress 追蹤** | onProgress callback | 即時進度回饋 |
| **Hook 系統** | toolHooks.ts | 可擴充的安全鉤子 |

### 6.4 具體遷移建議

1. **從 Tool 介面開始**：參考 Tool.ts 定義標準化介面
2. **重構現有工具**：遷移到 buildTool() 模式
3. **實現權限框架**：參考 permission rules 設計
4. **新增 Hook 通道**：預留 Pre/Post 鉤子點
5. **建立工具測試**：驗證 validateInput/checkPermissions

---

## 七、總結

Claude Code 的 Agent Tools 設計體現了幾個核心原則：

1. **Fail-Closed 預設**：預設行為安全（如 isConcurrencySafe=false）
2. **分層驗證**：validateInput → checkPermissions → Hooks
3. **彈性擴充**：lazySchema + feature() 閘道支援條件性功能
4. **統一介面**：buildTool 工廠模式簡化工具創建
5. **結果管理**：自動持久化、截斷、去重機制

這些模式可直接套用於 OpenClaw 的工具系統現代化。