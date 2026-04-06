# Claude Code CLI 狀態管理系統深度分析

> 分析日期：2026-04-02
> 來源：Claude Code CLI 洩漏原始碼（https://github.com/win4r/claude-code-2）

## 一、狀態管理架構

### 1.1 核心 Store 實作（`src/state/store.ts`）

```typescript
// 極簡函式式 Store，無任何外部依賴
export type Store<T> = {
  getState: () => T
  setState: (updater: (prev: T) => T) => void
  subscribe: (listener: Listener) => () => void  // 回傳取消訂閱函式
}

export function createStore<T>(initialState: T, onChange?: OnChange<T>): Store<T>
```

**設計特點**：
- **Pure TypeScript**：無需 Redux/MobX，僅用 `Set<Listener>` 實作發布-訂閱
- **Object.is 比較**：避免無意義的重新渲染
- **可選的 `onChange` hook**：狀態變更時觾發副作用（如寫入磁碟、通知外部系統）

### 1.2 AppState 與 React 整合（`src/state/AppState.tsx`）

```
AppStateProvider (React Context Provider)
    │
    ├── createStore(getDefaultAppState(), onChangeAppState)
    │
    ├── useAppState(selector) ─── useSyncExternalStore(store.subscribe, get, get)
    │                               只在 selector 返回值變化時觸發 re-render
    │
    ├── useSetAppState() ─────── store.setState（不訂閱，永不 re-render）
    │
    └── useAppStateStore() ───── 直接取得 store 本身（給非 React 程式碼用）
```

**關鍵創新**：用 `useSyncExternalStore` 將外部 store 接入 React，selector 模式只訂閱需要的 slice。

### 1.3 全域狀態快照（龐大的 `AppState` 類型）

`AppState` 涵蓋幾乎所有應用程式狀態：
- `settings`、`tasks`、`mcp`、`plugins`
- `speculation`、`promptSuggestion`、`fileHistory`
- `teamContext`、`standaloneAgentContext`
- `replBridge*`（Always-on bridge 狀態）

---

## 二、Session 生命週期

### 2.1 Session 持久化（`src/utils/sessionStorage.ts`）

Session 以 **JSONL 格式**保存在 `~/.claude/sessions/`：
- 每個訊息一行（user/assistant/system/attachment message）
- 包含 metadata（`sessionId`、`agentName`、`mode`）
- 支援 `parentUuid` chain（回覆追蹤）

### 2.2 Session 恢復流程（`ResumeConversation.tsx`）

```
選擇要恢復的 session
         │
         ▼
loadConversationForResume(log) ── 從磁碟讀取訊息
         │
         ├── switchSession(sessionId)
         ├── restoreSessionMetadata()
         ├── restoreAgentFromSession()
         ├── restoreWorktreeForResume()
         ├── adoptResumedSessionFile()
         └── CONTEXT_COLLAPSE feature → restoreFromEntries()
                   │
                   ▼
              <REPL screen> with initialMessages
```

---

## 三、Context 與 System Prompt 建構

### 3.1 Context 收集（`src/context.ts`）

```typescript
getSystemContext()   // 快取
  └── getGitStatus()       // branch, status, recent commits
  └── cacheBreaker         // ant-only 调试用

getUserContext()     // 快取
  └── getClaudeMds()       // .claude/ 目錄下的 memory 檔案
  └── currentDate          // 今天的日期
```

### 3.2 System Prompt 組裝（`REPL.tsx` 中 `buildEffectiveSystemPrompt`）

```typescript
const systemContext = await getSystemContext()
const userContext = await getUserContext()
const effectiveSystemPrompt = buildEffectiveSystemPrompt({
  systemPrompt, appendSystemPrompt, systemContext, userContext,
  mcpResources, sessionHooks, coordinatorContext,
})
```

**關鍵**：Context 是 **cached + composed**，不是每次 query 都重新收集。

---

## 四、可借鑒的設計模式

### Pattern 1：Selector-based Subscription（避免過度渲染）

```typescript
// ✅ 好：只訂閱 needed slice
const model = useAppState(s => s.mainLoopModel)

// ❌ 壞：返回新物件，永遠觸發 re-render
const { model, tasks } = useAppState(s => ({ ... }))
```

### Pattern 2：Side-effect Hook（狀態變更 → 外部效應）

```typescript
// store 的 setState 只更新記憶體
// onChange callback 處理所有持久化/同步副作用
createStore(initialState, onChangeAppState)
```

### Pattern 3：Branded Types（杜絕 ID 混淆）

```typescript
export type SessionId = string & { readonly __brand: 'SessionId' }
export type AgentId = string & { readonly __brand: 'AgentId' }
```

### Pattern 4：Feature-gated Code（Dead Code Elimination）

```typescript
const VoiceProvider = feature('VOICE_MODE')
  ? require('../context/voice.js').VoiceProvider
  : ({ children }) => children
```

### Pattern 5：JSONL > 資料庫

Session 用純文字 JSONL 存，簡單且易於调试，不需要 migration。

---

## 五、重點觀察

1. **JSONL > 資料庫**：Session 用純文字 JSONL 存，簡單且易於调试，不需要 migration
2. **Selector 是 React 效能關鍵**：所有 component 用 selector 訂閱，確保最小 re-render
3. **State 變更 = 純函式更新 + 可選 side-effect**：Store 本身無副作用，所有副作用在 `onChange` callback 中處理
4. **Session 恢復是 first-class 功能**：有專屬 `<ResumeConversation>` screen 和完整的恢復流程
5. **No 正式 state machine library**：狀態轉換散落在各 component/screen 中，沒有 XState 之類的 formal statechart
