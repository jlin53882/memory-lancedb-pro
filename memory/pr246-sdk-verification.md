# PR246 SDK 驗證結果

> 驗證日期：2026-04-02
> 測試專案：`C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test`

## 驗證結果表格

| 問題 | 答案 |
|------|------|
| recalledMemoryIds 欄位名 | **不存在** |
| recalledMemoryIds 定義位置 | N/A（SDK 中無此欄位）|
| agent_end hook 存在 | **是** |
| before_prompt_build hook 存在 | **是** |
| session_end hook 存在 | **是** |
| SDK 版本 | 2026.3.23-2 |

## 詳細說明

### 1. recalledMemoryIds 欄位

**結論：不存在於 SDK 中**

經過搜尋 OpenClaw Plugin SDK（`C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\dist\plugin-sdk`）的型別定義：
- 在 `types.d.ts` 的 `PluginHookAgentContext` 中**沒有** `recalledMemoryIds` 欄位
- SDK 提供的 context 僅包含：
  - `agentId`
  - `sessionKey`
  - `sessionId`
  - `workspaceDir`
  - `messageProvider`
  - `trigger`
  - `channelId`

在測試專案的 `index.ts` 中也**沒有**使用 `recalledMemoryIds`，而是用 `prependContext` 作為返回值傳遞 context 給 prompt。

### 2. Hooks 驗證

所有要求的 hooks 都存在於 SDK：

| Hook 名稱 | 位置 | 狀態 |
|-----------|------|------|
| `before_prompt_build` | types.d.ts:1554 | ✅ 存在 |
| `agent_end` | types.d.ts:1558 | ✅ 存在 |
| `session_end` | types.d.ts:1574 | ✅ 存在 |

### 3. SDK 版本

從全域安裝的 openclaw 取得：
```
openclaw@2026.3.23-2
```

## 結論與建議

1. **`ctx.session.recalledMemoryIds` 不可用** - 若需要在 agent end 時取得 recall 的 memory IDs，必須透過其他機制（如 plugin 內部 state）自行追蹤
2. **所有三個 hooks 都可用** - 可用於實作 Phase 2、Phase 3 的需求
3. **可用 `prependContext`** - SDK 的 `before_prompt_build` hook 可回傳 `prependContext` 屬性，這是目前傳遞 recall 結果的方式
