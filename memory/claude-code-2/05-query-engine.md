# Claude Code CLI Query Engine 深度分析

> 分析日期：2026-04-02
> 來源：Claude Code CLI 洩漏原始碼（https://github.com/win4r/claude-code-2）

## 一、Query Engine 架構流程圖

```
submitMessage(prompt)
         │
         ▼
fetchSystemPrompt() ──── System prompt 建構（含 tool/command/mcp context）
         │
         ▼
processUserInput() ─── Slash command 處理
         │
         ▼
query() Pipeline ──── 核心迴圈（AsyncGenerator）
         │
         ▼
┌──────────────────────────────────────────────────────┐
│                    Query Loop                          │
│                                                       │
│  SNIP Compact / Micro Compact / Auto Compact          │
│       │           │           │                      │
│       └───────────┴───────────┘                      │
│                    │                                  │
│                    ▼                                  │
│  callModel() ── Anthropic API Streaming              │
│       │                                               │
│       ├──→ tool_use blocks found? ──► Tool Call Loop │
│       └──→ text/thinking only ──► STOP_HOOKS_CHECK  │
│                                                       │
│  Stop Hooks / Recovery Logic                          │
│       │                                               │
│       ├── needsFollowUp=true ──► Next Turn Recursion │
│       └── needsFollowUp=false ──► Terminal          │
└──────────────────────────────────────────────────────┘
         │
         ▼
Yield Messages to SDK Caller
```

---

## 二、Tool Call Loop 狀態機

| 狀態 | 進入條件 | 處理邏輯 |
|------|----------|----------|
| `WAITING_MODEL_RESPONSE` | 每次 API 呼叫開始 | 等待 streaming response |
| `HAS_TOOL_USE_BLOCKS` | content_block 含 tool_use | 執行工具呼叫 |
| `EXECUTING_TOOLS` | 有 tool_use 區塊 | 依序或平行執行 |
| `STOP_HOOKS_CHECK` | Tool execution 完成 | 檢查攔截 hooks |
| `CONTINUE_TURN` | needsFollowUp=true | 遞迴呼叫 query() |
| `TERMINAL` | needsFollowUp=false | 返回結果 |

**Terminal 狀態種類**：
- `Completed`：正常結束
- `Aborted`：使用者中斷
- `MaxTurns`：turn 限制達到
- `MaxBudget`：USD 預算超出
- `PromptTooLong`：413 after recovery
- `ToolUseError`：工具執行失敗

---

## 三、Streaming Response 處理

```typescript
for await (const part of stream) {
  switch (part.type) {
    case 'message_start':
      usage = updateUsage(usage, part.message?.usage)
      break
    case 'content_block_start':
      contentBlocks[part.index] = { ...part.content_block }
      break
    case 'content_block_delta':
      switch (delta.type) {
        case 'input_json_delta':
          contentBlock.input += delta.partial_json
        case 'text_delta':
          contentBlock.text += delta.text
        case 'thinking_delta':
          contentBlock.thinking += delta.thinking
      }
      break
    case 'message_stop':
      this.totalUsage = accumulateUsage(this.totalUsage, usage)
      break
  }
}
```

**關鍵設計**：
- **分塊累積**：每個 content_block 獨立累積，避免 O(n²) 解析
- **Idle Watchdog**：90秒無資料自動中止 stream
- **TTFT 追蹤**：Time to First Token
- **Stall Detection**：30秒間距檢測，記錄停滯事件

---

## 四、Token Budget 追蹤（tokenBudget.ts）

```typescript
const COMPLETION_THRESHOLD = 0.9  // 90% 時觸發
const DIMINISHING_THRESHOLD = 500   // 每 turn  progress 門檻
```

---

## 五、可借鑒的實作細節

### 1. 三層 Context Compression

| 層次 | 觸發時機 | 策略 |
|------|---------|------|
| SNIP Compact | API 413 error | 移除最後一條訊息 |
| Micro Compact | 每 N 回合 | 折疊連續同角色訊息 |
| Auto Compact | 90% token budget | 總結對話 |

### 2. Stop Hooks 機制

Tool execution 完成後檢查 `stop_*` hooks，決定是否 inject recovery 訊息並繼續迴圈。

### 3. Context 組裝

```typescript
const effectiveSystemPrompt = buildEffectiveSystemPrompt({
  systemPrompt, appendSystemPrompt, systemContext, userContext,
  mcpResources, sessionHooks, coordinatorContext,
})
```

---

## 六、與 OpenClaw 對比

| 面向 | Claude Code | OpenClaw |
|------|------------|----------|
| Streaming | 完整處理 content_block delta | 未知 |
| Tool Loop | 完整狀態機 | 部分類似 |
| Context Compression | 三層（SNIP/Micro/Auto）| 僅 Auto Compact |
| Token Budget | 90% 門檻主動壓縮 | 被動等待 413 |
| Recovery | 413 後 inject recovery | 未知 |
