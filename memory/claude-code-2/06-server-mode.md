# Claude Code CLI — Server Mode 深度分析報告

> 分析目標 repo：https://github.com/win4r/claude-code-2
> 分析時間：2026-04-02
> 分析者：OpenClaw Agent（subagent 任務）

---

## 一、Server Mode 架構

### 1.1 兩種 Server 模式

Claude Code 的 Server Mode 存在**兩條路徑**，代表不同代際的設計：

| 特性 | v1（傳統） | v2（CCR v2）|
|------|-----------|-------------|
| 傳輸層 | `HybridTransport`（WebSocket + HTTP POST） | `SSETransport` 讀 + `CCRClient` 寫 |
| 認證 | OAuth Bearer Token（直接寫入 env） | Worker JWT（每次 /bridge 置換）|
| 用途 | 舊版 remote-control | 新版 REPL Bridge、daemon |

**v2 的核心價值**：廢除 Environments API 的 poll/dispatch 層，讓 REPL 模式直接與 session-ingress 層互動，大幅降低延遲。

### 1.2 Direct Connect 模式（`src/server/`）

`DirectConnectManager` 負責從 Web UI 啟動本機 session，流程為：

1. **建立 session**：POST `/v1/code/sessions`（OAuth）
2. **取得 session JWT**：POST `/v1/code/sessions/{id}/bridge` → `{ worker_jwt, expires_in, api_base_url, worker_epoch }`
3. **啟動 transport**：使用 `buildCCRv2SdkUrl()` 建出的 URL，透過 `createV2ReplTransport()` 建立 SSE + CCRClient
4. **主動刷新 JWT**：`createTokenRefreshScheduler()` 在 JWT 過期前 5 分鐘自動重新呼叫 `/bridge` 取得新 epoch

```typescript
// initEnvLessBridgeCore 的核心流程（remoteBridgeCore.ts）
// 1. POST /v1/code/sessions → sessionId
// 2. POST /v1/code/sessions/{id}/bridge → worker_jwt + expires_in
// 3. createV2ReplTransport({ sessionUrl, ingressToken, epoch })
// 4. createTokenRefreshScheduler → 5min 前觸發被動刷新
```

### 1.3 訊息轉換層（`sdkMessageAdapter.ts`）

CCR 後端以 SDK 原型格式發送訊息，REPL 需轉換為內部 `Message` 類型：

- `SDKAssistantMessage` → `AssistantMessage`
- `SDKPartialAssistantMessage` → `StreamEvent`（串流事件）
- `SDKResultMessage` → `SystemMessage`（成功/失敗）
- `SDKSystemMessage`（init/status/compact_boundary）→ `SystemMessage`
- `SDKToolProgressMessage` → `SystemMessage`
- `SDKUserMessage` → 工具結果偵測（透過 content 形狀判斷是否為 tool_result）

**工具結果偵測邏輯**（非常精細）：
```typescript
// 不是用 parent_tool_use_id（伺服器端 normalizeMessage 會將其 hardcode 為 null）
// 而是用 content 形狀偵測
const isToolResult = Array.isArray(content) && 
  content.some(b => b.type === 'tool_result')
```

---

## 二、遠端協作機制（Remote Session）

### 2.1 兩種遠端 Bridge 架構

**環境型 Bridge（`bridgeMain.ts` / `runBridgeLoop`）**：

```
┌─────────────────────────────────────────────────┐
│           Claude.ai / Web UI                    │
└──────────┬──────────────────────────────────────┘
           │  poll / work dispatch
┌──────────▼──────────────────────────────────────┐
│  Bridge（standalone CLI）                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────┐│
│  │ pollForWork │→│ SessionSpawn │→│  Child  ││
│  │   (API)     │  │   (fork)    │  │  CLI    ││
│  └─────────────┘  └──────────────┘  └─────────┘│
└─────────────────────────────────────────────────┘
           │  /v1/environments/{id}/work/poll
┌──────────▼──────────────────────────────────────┐
│       Environments API（Redis + Firestore）       │
└─────────────────────────────────────────────────┘
```

**REPL 型 Bridge（`remoteBridgeCore.ts` / `initEnvLessBridgeCore`）**：

```
┌──────────────────────────────────────────────────┐
│            Claude.ai / Web UI                     │
└──────────┬───────────────────────────────────────┘
           │  WebSocket（SSE stream）
┌──────────▼───────────────────────────────────────┐
│  REPL（本地 CLI）                                 │
│  ┌─────────────────────────────────────────────┐ │
│  │ SessionsWebSocket（v1）/SSETransport（v2）   │ │
│  │ writeBatch → CCRClient → /worker/events     │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
           │  POST /v1/code/sessions/{id}/bridge
┌──────────▼───────────────────────────────────────┐
│        Session Ingress（直接，無 Environments 層） │
└──────────────────────────────────────────────────┘
```

### 2.2 Session 生命週期（Bridge 環境）

`runBridgeLoop` 的核心狀態機：

1. **`registerBridgeEnvironment`** → 取得 `environment_id` + `environment_secret`
2. **`pollForWork`** → 長輪詢 work queue（可配置 reclaim window）
3. **`acknowledgeWork`** → 明確 ack 後才視為已接收（避免丟失 work）
4. **Spawn child CLI** → 子程序繼承 bridge 的 OAuth token
5. **`stopWorkWithRetry`** → 最多 3 次重試（1s/2s/4s exponential backoff）
6. **`archiveSession`** → 工作結束後歸檔（idempotent，409 即已歸檔）

**Multi-session 支援**（GrowthBook `tengu_ccr_bridge_multi_session` gate）：
- `--spawn=worktree`：每個 session 隔離於獨立 git worktree
- `--spawn=same-dir`：多個 session 共享目錄
- `--spawn=session`（legacy）：經典單一 session 模式
- 支援 `--capacity N` 設定最大併發數（預設 32）

### 2.3 Session 遷移與恢復

**Crash Recovery Pointer**（`bridgePointer.json`）：
- 單一 session 模式下寫入 `~/.claude/bridge-pointer.json`
- 包含 `{ sessionId, environmentId, source }`
- 啟動時偵測 sleep/wake（gap > 2×backoff cap → 重置 error budget）

**工作搶占偵測**：
- `completedWorkIds` Set 追蹤已完成的 work item，避免 server 重新發送已處理的 work
- `reconnectSession` 在 JWT 過期後觸發 server 端重新分發

---

## 三、安全模型分析

### 3.1 認證三層架構

| 層 | 憑證 | 生命週期 | 用途 |
|----|------|---------|------|
| **OAuth** | Bearer Token（登入取得）| ~4 小時 | CLI → API 認證 |
| **Session Ingress JWT** | Bearer Token（/bridge 取得）| 動態（伺服器指定）| WebSocket/SSE 訂閱 |
| **Environment Secret** | 靜態字串 | 環境生命週期 | poll/ack/heartbeat API 呼叫 |

### 3.2 Trusted Device 機制（`trustedDevice.ts`）

**兩段式 Feature Flag**：
1. `tengu_sessions_elevated_auth_enforcement`（CLI 端）：控制是否傳送 `X-Trusted-Device-Token`
2. Server-side flag：控制是否在 JWT 核發時強制驗證 trusted device

**登記流程**：
- 只能在 `/login` 後 10 分鐘內呼叫（`account_session.created_at < 10min`）
- Token 持久化於 keychain（90 天滾動）
- 清除时机：logout 時

**轉送 Header**：
```typescript
// bridgeApi.ts getHeaders()
const deviceToken = deps.getTrustedDeviceToken?.()
if (deviceToken) {
  headers['X-Trusted-Device-Token'] = deviceToken
}
```

### 3.3 JWT 被動刷新機制（`jwtUtils.ts`）

`createTokenRefreshScheduler` 的核心設計：

```typescript
// 調度策略：
// 1. 讀取 JWT 的 exp claim，解碼後計算延遲
// 2. 到期前 5 分鐘（TOKEN_REFRESH_BUFFER_MS）觸發
// 3. 無法解碼時（OAuth token）：30 分鐘 fallback interval
// 4. Generation counter 防止並發刷新造成 race condition
// 5. MAX_REFRESH_FAILURES=3 次連續失敗後放棄
// 6. REFRESH_RETRY_DELAY_MS=60s 重試間隔
```

**Generation Counter（防止 ABA race）**：
```typescript
// 每次 schedule() 遞增 generation；doRefresh() 執行前檢查是否已過期
// 如果 schedule() 在 doRefresh() async 等待期間被呼叫，generation 會不同
if (generations.get(sessionId) !== gen) {
  return  // 已過期，跳過
}
```

### 3.4 連線安全

- **HTTPS 強制**：非 localhost 目標必須使用 HTTPS
- **mTLS 支援**：`getWebSocketTLSOptions()` 支援客戶端憑證
- **Proxy 支援**：`getWebSocketProxyAgent()` / `getWebSocketProxyUrl()`
- **ptrace 防止**：`setNonDumpable()` 在 Linux 上呼叫 `prctl(PR_SET_DUMPABLE, 0)` 阻止同 UID 下的 ptrace

### 3.5 Path Traversal 防護

所有 server 提供的 ID（`environment_id`、`workId`、`sessionId`）在用於 URL path 前都會驗證：

```typescript
// bridgeApi.ts
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/
export function validateBridgeId(id: string, label: string): string {
  if (!id || !SAFE_ID_PATTERN.test(id)) {
    throw new Error(`Invalid ${label}: contains unsafe characters`)
  }
  return id
}
```

---

## 四、IDE Bridge 訊息協定

### 4.1 Bridge API 端點（`bridgeApi.ts`）

| 端點 | 方法 | 認證 | 用途 |
|------|------|------|------|
| `/v1/environments/bridge` | POST | OAuth | 註冊 bridge 環境 |
| `/v1/environments/{id}/work/poll` | GET | Environment Secret | 輪詢 work 佇列 |
| `/v1/environments/{id}/work/{workId}/ack` | POST | Session Ingress JWT | 確認 work 已接收 |
| `/v1/environments/{id}/work/{workId}/stop` | POST | OAuth | 停止 work item |
| `/v1/environments/{id}/work/{workId}/heartbeat` | POST | Session Ingress JWT | 延長 lease |
| `/v1/environments/bridge/{envId}` | DELETE | OAuth | 註銷環境 |
| `/v1/sessions/{id}/archive` | POST | OAuth | 歸檔 session |
| `/v1/environments/{id}/bridge/reconnect` | POST | OAuth | 重新分發 session |
| `/v1/sessions/{id}/events` | POST | Session Ingress JWT | 發送 permission 響應 |

### 4.2 SDK 訊息類型

**Inbound（WebSocket/SSE 接收）**：
- `SDKMessage`（discriminated union）：
  - `assistant`：完整 assistant 訊息
  - `user`：使用者訊息或工具結果
  - `stream_event`：串流事件（partial assistant、thinking 區塊等）
  - `result`：工作單元結束（success/error）
  - `system`：系統訊息（init/status/compact_boundary）
  - `tool_progress`：工具執行進度
  - `tool_use_summary`：工具使用摘要
  - `rate_limit_event`：速率限制事件
  - `auth_status`：認證狀態

**Outbound（HTTP POST 發送）**：
- `SDKControlRequest`：伺服器發起的控制請求
  - `initialize`：session 初始化
  - `set_model`：變更模型
  - `set_max_thinking_tokens`：變更 thinking 預算
  - `set_permission_mode`：變更權限模式
  - `interrupt`：中斷目前工作
  - `can_use_tool`：工具使用確認
- `SDKControlResponse`：控制請求響應
- `SDKControlCancelRequest`：取消 pending 請求

### 4.3 Echo 去重機制（`BoundedUUIDSet`）

```typescript
// 防止自己發送的訊息被 server echo 回來
// 使用 FIFO ring buffer，容量固定 O(capacity)
// 兩層去重：
// 1. recentPostedUUIDs：我們發出的訊息 UUID（outbound echo）
// 2. recentInboundUUIDs：已轉送的 inbound 訊息 UUID（server 重新分發）
export class BoundedUUIDSet {
  private ring: (string | undefined)[]  // 固定容量環形緩衝
  private set = new Set<string>()        // O(1) 查詢

  add(uuid: string): void {
    // 驅逐最舊的 entry 並從 set 中移除
  }
}
```

### 4.4 FlushGate（順序保證）

在 history flush 期間，所有新訊息進入排隊，直到 flush 完成後按序發送：

```typescript
// remoteBridgeCore.ts
const flushGate = new FlushGate<Message>()
// writeMessages 時：
if (flushGate.enqueue(...filtered)) {
  return  // 已排隊，稍後 drain
}
// drain 時：
const msgs = flushGate.end()  // FIFO 取出所有排隊訊息
void transport.writeBatch(events)
```

---

## 五、連線中斷與恢復

### 5.1 SessionsWebSocket 重連策略（`SessionsWebSocket.ts`）

```typescript
const RECONNECT_DELAY_MS = 2000
const MAX_RECONNECT_ATTEMPTS = 5
const MAX_SESSION_NOT_FOUND_RETRIES = 3  // 4001 特殊處理

// 重連邏輯：
// 1. 永久關閉碼（4003 unauthorized）→ 不重連
// 2. 4001（session not found）→ 最多 3 次重試（可能是 compaction 期間的短暫不一致）
// 3. 其他情況 → 指數退避重連，最多 5 次

PERMANENT_CLOSE_CODES = new Set([4003])

// Ping/Pong 心跳：30 秒一次
const PING_INTERVAL_MS = 30000
```

### 5.2 v2 Transport 重建（`rebuildTransport`）

```typescript
// rebuildTransport 的觸發時機：
// 1. JWT 被動刷新（到期前 5 分鐘）
// 2. 401 認證失敗（OAuth token 過期）
// 3. 409 epoch 不匹配（伺服器端 epoch 已更新）

// 重建時的序列號攜帶：
const seq = transport.getLastSequenceNum()  // 取得 SSE high-water mark
transport = await createV2ReplTransport({ initialSequenceNum: seq, ... })
// 新 transport 連接時傳送 Last-Event-ID，伺服器從該位置繼續
```

### 5.3 Sleep/Wake 偵測

```typescript
// bridgeMain.ts poll loop
// 如果距上次錯誤的時間差 > 2 × connBackoffCap，視為 sleep/wake
// 重置所有 error budget，避免 wake 後被舊的 backoff 延遲卡住
if (now - lastPollErrorTime > pollSleepDetectionThresholdMs(backoffConfig)) {
  connBackoff = 0
  generalBackoff = 0
  // 重置連線錯誤追蹤
}
```

### 5.4 Health Check Work

Bridge 支援 `healthcheck` 類型的 work item，用於：
- 驗證環境是否仍可達
- 觸發 lease 續約
- 不需要啟動完整 CLI 子程序

---

## 六、Upstream Proxy 機制（`src/upstreamproxy/`）

### 6.1 設計目標

在 CCR container 內執行時，將外發 HTTPS 流量導向企業 proxy，以注入監控（Datadog）和認證凭證。

### 6.2 架構

```
CLI subprocess        本地 CLI            CCR Container
┌──────────────┐   ┌────────────────┐   ┌──────────────────────┐
│ curl / gh    │──→│ CONNECT relay  │──→│ WebSocket tunnel      │
│ (HTTP CLIENT)│   │ (127.0.0.1:N)  │   │ /v1/code/upstreamproxy/ws
└──────────────┘   └────────────────┘   └──────────┬───────────┘
                                                   │ MITM + inject
                                           ┌───────▼───────────┐
                                           │ CCR upstreamproxy │
                                           │ (inject creds)   │
                                           └───────┬───────────┘
                                                   │ 企業 proxy
                                           ┌───────▼───────────┐
                                           │ upstream service   │
                                           └───────────────────┘
```

### 6.3 安全措施

1. **`prctl(PR_SET_DUMPABLE, 0)`**：Linux 阻止同 UID ptrace，防止 `gdb -p $PPID` 洩露 heap 中的 token
2. **Token file 及時刪除**：`unlink(session_token)` 在 relay 確認啟動後執行
3. **NO_PROXY 白名單**： Anthropic API、GitHub、npm、PyPI 等不走 MITM proxy
4. **CA Bundle 拼接**：下載 CCR CA + 拼接系統 CA bundle，確保各 runtime（curl/gh/Python/Node）都信任 MITM 憑證

### 6.4 WebSocket 協定

- **編碼**：`protobuf UpstreamProxyChunk`（手動 varint 編碼，無需 protobufjs 依賴）
- **認證**：Basic auth（`sessionId:token`）在 WebSocket upgrade 時傳送 Bearer，在 CONNECT 內文傳送 Basic
- **Chunk 大小**：512KB 上限

---

## 七、可借鑒到 OpenClaw 的設計

### 7.1 JWT 被動刷新 + Generation Counter

**現況**：OpenClaw 目前依賴 cron 定期重新整理 token，沒有考慮並發刷新和 race condition。

**借鑒**：
```typescript
// 每次 schedule 遞增 generation；doRefresh 執行時檢查是否過期
// 避免：舊的 doRefresh 在新的 schedule 完成後才執行完，覆蓋新 token
```

**適用場景**：OpenClaw 的 MCP server 連線管理、Discord/Telegram bot 的 OAuth token 刷新。

### 7.2 BoundedUUIDSet Echo 去重

**現況**：OpenClaw 目前沒有對 outbound 訊息的 echo 去重機制。

**借鑒**：
- 使用固定容量 ring buffer，記憶體 O(capacity)
- outbound 訊息 UUID 存入 set，收到後比對
- 防止 server echo 回來的自己發的訊息被重複處理

**適用場景**：OpenClaw 的 Discord/Telegram 回應去重、WebSocket 訊息處理。

### 7.3 FlushGate 訊息順序保證

**現況**：OpenClaw 在歷史訊息 flush 時沒有隔離機制，可能造成新訊息搶先於歷史訊息發送。

**借鑒**：
- flush 期間所有寫入進入 gate 排隊
- flush 完成後一次性發送排隊訊息
- 確保 `[history..., live...]` 順序

**適用場景**：OpenClaw 啟動時的對話歷史同步、跨 Agent 訊息轉發。

### 7.4 Sleep/Wake 偵測

**現況**：OpenClaw 的 heartbeat/cron 在筆記型電腦 sleep/wake 後可能失效，沒有自動重置機制。

**借鑒**：
- 追蹤上次錯誤時間
- 如果 gap > 2×backoff cap，視為 sleep/wake，重置 error budget
- 避免 wake 後被累積的 backoff 卡住

**適用場景**：OpenClaw 的健康檢查 cron、Discord/Telegram long-polling。

### 7.5 Bridge 環境的多worker 架構

**現況**：OpenClaw 目前是單一 CLI 實例，沒有類似 Environments API 的 work queue 機制。

**借鑒**：
- 將 OpenClaw 的工作接受機制抽象為環境註冊 + work poll 模式
- 支援多 session（worktree isolation）用於並行任務
- session 完成後自動 archive，環境可持續服務

**適用場景**：OpenClaw 的多租戶工作分配、containerized 部署。

### 7.6 Path Traversal 防護模式

**現況**：OpenClaw 在組合外部 URL 時可能未驗證 ID 字元。

**借鑒**：
```typescript
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/
if (!SAFE_ID_PATTERN.test(id)) throw new Error(`Invalid ${label}`)
```

### 7.7 Trusted Device Token（進階）

如果 OpenClaw 未來要支援企業 SSO + 設備信任：
- 兩段式 Feature Flag（CLI + Server 各自控制）
- 設備 Token 持久化於 keychain（而非記憶體）
- 在 login 後短時間內完成 enrollment

---

## 八、附錄：核心檔案索引

| 檔案 |職責 |
|------|-----|
| `src/server/types.ts` | Direct connect session 類型定義 |
| `src/server/directConnectManager.ts` | 從 Web UI 啟動 direct connect session |
| `src/server/createDirectConnectSession.ts` | 創建 direct connect session 的 HTTP 流程 |
| `src/remote/RemoteSessionManager.ts` | 遠端 session 生命週期管理 |
| `src/remote/SessionsWebSocket.ts` | v1 WebSocket 訂閱客戶端（含重連） |
| `src/remote/sdkMessageAdapter.ts` | SDKMessage ↔ REPL Message 轉換 |
| `src/remote/remotePermissionBridge.ts` | 遠端工具使用確認（合成 AssistantMessage）|
| `src/bridge/bridgeMain.ts` | Standalone remote-control 入口點 |
| `src/bridge/remoteBridgeCore.ts` | REPL Bridge 核心（v2，無 Environments API）|
| `src/bridge/bridgeApi.ts` | Bridge API 客戶端（所有 /environments/* 端點）|
| `src/bridge/bridgeMessaging.ts` | 訊息路由、ingress 解析、echo 去重 |
| `src/bridge/jwtUtils.ts` | JWT 解碼、被動刷新調度器 |
| `src/bridge/replBridgeTransport.ts` | v1/v2 transport 適配器（HybridTransport ↔ SSE+CCRClient）|
| `src/bridge/trustedDevice.ts` | Trusted device token 讀取與 enrollment |
| `src/bridge/workSecret.ts` | Work secret 解碼、SDK URL 建構、worker 註冊 |
| `src/bridge/types.ts` | Bridge 層核心類型定義 |
| `src/upstreamproxy/upstreamproxy.ts` | Container 端 upstream proxy 初始化 |
| `src/upstreamproxy/relay.ts` | HTTP CONNECT → WebSocket relay 實作 |

---

*本報告由 OpenClaw subagent 分析生成，分析時間：2026-04-02*
