# Flet 訊息系統（PubSub / Session）— 學習筆記

> 程式碼版本：Flet 0.82.2
> 閱讀日期：2026-03-23
> 程式碼來源：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\`

---

## PubSub 的角色與使用場景

### 架構概覽

PubSub 系統由兩個類別分工：

| 類別 | 檔案 | 職責 |
|------|------|------|
| `PubSubHub` | `pubsub/pubsub_hub.py` | 程序級（process-wide）Router，持有所有订阅者的索引 |
| `PubSubClient` | `pubsub/pubsub_client.py` | Session 級 Facade，包住 `PubSubHub` + `session_id` |

```
┌─────────────────────────────────────────────────┐
│                  PubSubHub (單例)                │
│                                                  │
│  __subscribers: {session_id → set[handler]}       │
│  __topic_subscribers: {topic → {session_id → h}} │
│  __subscriber_topics: {session_id → {topic → h}} │
└────────────────────┬────────────────────────────┘
                     │ 一個 session 一個 client
        ┌────────────┴────────────┐
   PubSubClient            PubSubClient
   (session A)             (session B)
```

### 什麼是「頁面間/應用內廣播」

在 Flet 桌面模式下，**一個 Flet 應用只有一個 WebSocket 連線（綁定一個 session）**，但 PubSubHub 是程序級的廣播器，適用於：

- 多視窗應用（多個 client 連到同一 server 程式）
- 在同一個 Page 內，不同元件之間的通訊（透過同一 session 的 handler）
- 跨 session 的全域廣播（`send_all`）

> **注意**：在瀏覽器模式下，每個分頁是不同的 client/連線，PubSubHub 仍然有效。

### Hub 的資料結構（三層索引）

`pubsub_hub.py` 第 24-35 行：

```python
self.__subscribers: dict[str, set[Callable]] = {}
# key: session_id, value: 全域 handler 集合

self.__topic_subscribers: dict[str, dict[str, set[Callable]]] = {}
# key: topic → session_id → handlers（正向索引）

self.__subscriber_topics: dict[str, dict[str, set[Callable]]] = {}
# key: session_id → topic → handlers（反向索引，用於快速清理）
```

雙向索引的設計是為了解動機 `unsubscribe_all` 時可以快速找到某個 session 訂閱的所有 topic。

### 訊息發送內部機制

`__send()` 方法（第 189-212 行）負責 dispatch：

```python
def __send(self, handler, args):
    if inspect.iscoroutinefunction(handler):
        # async handler → 跨執行緒排程到 hub 的 event loop
        asyncio.run_coroutine_threadsafe(handler(*args), self.__loop)
    else:
        if self.__executor:
            # sync handler → 丢給執行緒池
            self.__loop.run_in_executor(self.__executor, handler, *args)
        else:
            # 無 executor → 同步調用
            handler(*args)
```

---

## page.pubsub API

### Session 取得 PubSubClient

`Session` 在初始化時（第 42 行 `session.py`）建立自己的 `PubSubClient`：

```python
self.__pubsub_client = PubSubClient(conn.pubsubhub, self.__id)
```

外部透過 `page.pubsub` 屬性（第 93-99 行）取得：

```python
@property
def pubsub_client(self) -> PubSubClient:
    return self.__pubsub_client
```

### PubSubClient 所有 API

| 方法 | 作用 | 底層呼叫 |
|------|------|----------|
| `send_all(message)` | 廣播到**所有 session** 的全域訂閱者 | `pubsubhub.send_all()` |
| `send_all_on_topic(topic, message)` | 廣播到所有訂閱某 topic 的 session | `pubsubhub.send_all_on_topic()` |
| `send_others(message)` | 廣播到**除自己以外**的所有 session | `pubsubhub.send_others(session_id)` |
| `send_others_on_topic(topic, message)` | 廣播到除自己以外訂閱該 topic 的 session | `pubsubhub.send_others_on_topic()` |
| `subscribe(handler)` | 訂閱全域訊息（handler 收到 1 個參數：`message`） | `pubsubhub.subscribe()` |
| `subscribe_topic(topic, handler)` | 訂閱某 topic（handler 收到 2 個參數：`(topic, message)`） | `pubsubhub.subscribe_topic()` |
| `unsubscribe()` | 取消全域訂閱 | `pubsubhub.unsubscribe()` |
| `unsubscribe_topic(topic)` | 取消特定 topic 訂閱 | `pubsubhub.unsubscribe_topic()` |
| `unsubscribe_all()` | 取消所有訂閱（全域＋所有 topic） | `pubsubhub.unsubscribe_all()` |

### Topic 訂閱的內部維護邏輯

`subscribe_topic` 時（`pubsub_hub.py` 第 112-139 行），同時寫入兩個 dict：
- `__topic_subscribers[topic][session_id]` = handler set（新 topic 會建立新 dict）
- `__subscriber_topics[session_id][topic]` = handler set

這樣 unsubscribe 時可以快速反向查到所有 topic。

### Session 關閉時的 cleanup

`Session.close()` 方法（第 179-193 行 `session.py`）會自動调用：

```python
self.__pubsub_client.unsubscribe_all()
```

---

## Session 生命週期

### Session 的建立

`FletSocketServer.__on_message()` 收到 `REGISTER_CLIENT` 時（第 281-315 行 `flet_socket_server.py`）：

1. 新建 `Session(self)`（自己作為 Connection 傳入）
2. 若為重新連線（`req.session_id` 非空），跳過初始 patch
3. 執行 `before_main` 回調（用戶註冊的 main 函式）
4. 回送 `RegisterClientResponseBody`（含 session_id、page_patch、error）
5. 若有錯誤，發送 `SESSION_CRASHED` 給 client

### Session 的組成

每個 `Session` 包含：

| 成員 | 類型 | 說明 |
|------|------|------|
| `__conn` | `Connection` | 底層傳輸（目前是 `FletSocketServer`） |
| `__id` | `str` | 16 字元隨機 ID |
| `__page` | `Page` | 根頁面，Session 建立時同步建立 |
| `__index` | `WeakValueDictionary[int, BaseControl]` | 控制項 ID → 控制項實例的弱引用索引 |
| `__store` | `SessionStore` | Session 級 key-value 儲存 |
| `__pubsub_client` | `PubSubClient` | 綁定此 session 的 PubSub client |
| `__method_calls` | `dict[str, asyncio.Event]` | 等待 client 回應的 invoke-method 請求 |
| `__pending_updates` | `set[BaseControl]` | 待處理的延遲更新佇列 |
| `__pending_effects` | `list` | 待處理的 effect hook 佇列 |
| `__updates_task` | `asyncio.Task` | 背景更新排程器任務 |

### Session 的連線/斷線生命週期

#### 連線（connect）
`Session.connect()` → `attach_connection()` → 設定 `__conn` → 清空 `expires_at` →  flush 發送緩衝區 → dispatch `connect` 事件

#### 斷線（disconnect）
`Session.disconnect(session_timeout_seconds)`：
1. 設定 `expires_at = now + session_timeout_seconds`
2. 清空 `__send_buffer`（斷線期間的增量訊息丢棄）
3. 清空 `__pending_updates` 和 `__pending_effects`
4. 呼叫 `__conn.dispose()` 釋放連線資源
5. 設定 `__conn = None`
6. dispatch `disconnect` 事件

#### 關閉（close）
`Session.close()`：
1. 設定 `__closed = True`
2. 取消 `__updates_task`
3. `pubsub_client.unsubscribe_all()`（移除所有 PubSub 訂閱）
4. 取消所有等待中的 `invoke_method` 呼叫（设為 "Session closed" error）
5. dispatch `close` 事件

### 訊息發送緩衝機制

`Session.__send_message()` 方法（第 378-390 行）：

```python
def __send_message(self, message):
    if self.__conn:
        # 已連線 → 直接發送
        self.__conn.send_message(message)
    elif self.__expires_at is not None:
        # 已斷線但還在期限內 → 丢棄增量流量（避免緩衝區無限增長）
        return
    else:
        # 連線中但還沒設定 conn（如剛建立）→ 緩衝
        self.__send_buffer.append(message)
```

### Session 垃圾回收警告

第 50-52 行：
```python
weakref.finalize(
    self, lambda: logger.info(f"Session was garbage collected: {session_id}")
)
```

---

## WebSocket Protocol

### 傳輸層

`FletSocketServer`（`flet_socket_server.py`）同時支援兩種傳輸：

| 環境 | 傳輸方式 |
|------|----------|
| Windows 或 `port > 0` | TCP Socket |
| 非 Windows 且 `port == 0` | Unix Domain Socket（UDS） |

`start()` 方法第 88-113 行判定邏輯。

### 編解碼：MessagePack

協議採用 [MessagePack](https://msgpack.org/) 二進位格式（第 253-268 行）：

```python
# 發送編碼
m = msgpack.packb(
    [message.action, message.body],
    default=configure_encode_object_for_msgpack(BaseControl),
)

# 接收解碼（with custom ext_hook）
unpacker = msgpack.Unpacker(ext_hook=decode_ext_from_msgpack)
```

### 自定義 Extension Types

`decode_ext_from_msgpack()`（`protocol.py` 第 110-122 行）處理 4 種擴充類型：

| Ext Code | Python 類型 | 編碼格式 |
|----------|------------|---------|
| 1 | `datetime` | ISO format string |
| 2 | `time` | `"HH:MM"` string |
| 3 | `Duration` | microseconds (int) |
| 4 | `str` | UTF-8 bytes |

### 訊息框架格式

所有客戶端↔伺服器訊息都是 **2-element list**：

```
[action_code: int, body: dict]
```

`action_code` 對應 `ClientAction` 列舉（`protocol.py` 第 127-157 行）：

| Action | Code | 方向 | 說明 |
|--------|------|------|------|
| `REGISTER_CLIENT` | 1 | C→S / S→C | 客戶端註冊（含 page snapshot） |
| `PATCH_CONTROL` | 2 | S→C | 控制項樹差異補丁 |
| `CONTROL_EVENT` | 3 | C→S | 控制項事件通知 |
| `UPDATE_CONTROL_PROPS` | 4 | C→S | 客戶端更新控制項屬性 |
| `INVOKE_METHOD` | 5 | S→C / C→S | 雙向方法呼叫（帶 call_id） |
| `SESSION_CRASHED` | 6 | S→C | 嚴重錯誤通知 |

### 主要訊息 Body 結構

#### REGISTER_CLIENT（C→S）
```python
@dataclass
class RegisterClientRequestBody:
    session_id: str      # 空字串表示新 session
    page_name: str       # URL 邏輯名稱
    page: dict           # 初始 page 狀態快照
```

#### REGISTER_CLIENT（S→C）
```python
@dataclass
class RegisterClientResponseBody:
    session_id: str      # 伺服器分配的 session ID
    page_patch: Any      # 初始 page 補丁
    error: str           # 啟動錯誤，空表示成功
```

#### CONTROL_EVENT（C→S）
```python
@dataclass
class ControlEventBody:
    target: int          # 發出事件的控制項 ID
    name: str            # 事件名（無 on_ 前綴）
    data: Any            # 事件資料
```

#### INVOKE_METHOD（S→C 請求 / C→S 回應）
```python
# 請求
@dataclass
class InvokeMethodRequestBody:
    control_id: int
    call_id: str         # 用於關聯回應
    name: str
    args: dict

# 回應
@dataclass
class InvokeMethodResponseBody:
    control_id: int
    call_id: str
    result: Any
    error: str
```

### Socket I/O 迴圈

**接收迴圈**（`__receive_loop`，第 231-252 行）：
- 一次讀取最多 1MB，迴圈餽入 `msgpack.Unpacker`
- 每個完整訊息触发 `__on_message()`
- 連線 token 失效時立即 return（防止處理已更換連線的舊訊息）

**發送迴圈**（`__send_loop`，第 254-275 行）：
- 從 `asyncio.Queue` 取出預編碼的 MsgPack bytes
- 寫入 socket 並 `drain()`

### 連線替換機制（單客戶端模型）

`handle_connection()` 第 165-201 行：`FletSocketServer` 只允許**一個活躍連線**。

新連線到來時：
1. 取得 `__connection_lock`
2. 終結舊連線（`__terminate_active_connection_locked(reason="replaced")`）
3. 啟動新的 receive/send 任務
4. 舊任務自動被 cancel

舊連線斷線時（`writer.close()`）：
- `receive_loop` 收到 EOF → 退出
- `__on_message` 觸發 `__terminate_active_connection_locked(reason="client_disconnected")`

---

## 常用程式碼範例

### 基本 PubSub 全域廣播

```python
import flet as ft

def main(page: ft.Page):
    def on_message(message):
        page.add(ft.Text(f"收到廣播: {message}"))

    # 訂閱全域訊息
    page.pubsub.subscribe(on_message)

    def broadcast(e):
        # 向所有 session 廣播
        page.pubsub.send_all(f"Hello from {page.session_id}")

    page.add(ft.ElevatedButton("廣播", on_click=broadcast))

ft.app(main)
```

### Topic 訂閱

```python
def main(page: ft.Page):
    def on_chat_message(topic, message):
        page.add(ft.Text(f"[{topic}] {message}"))

    # 訂閱 "chat" topic，handler 收到 (topic, message)
    page.pubsub.subscribe_topic("chat", on_chat_message)

    def send_to_chat(e):
        page.pubsub.send_all_on_topic("chat", "新訊息")

    page.add(ft.ElevatedButton("發送", on_click=send_to_chat))

ft.app(main)
```

### 排除自己的廣播

```python
def main(page: ft.Page):
    page.pubsub.subscribe(lambda msg: page.add(ft.Text(f"其他人: {msg}")))
    page.pubsub.send_others("這是測試訊息")  # 自己的 handler 不會收到
```

### Session Store（Session 級 Key-Value 儲存）

```python
def main(page: ft.Page):
    page.session.store.set("username", "Alice")
    page.session.store.set("count", 0)

    # 讀取
    name = page.session.store.get("username")  # "Alice"
    count = page.session.store.get("count")    # 0

    # 檢查
    if page.session.store.contains_key("username"):
        page.add(ft.Text(name))

    # 刪除
    page.session.store.remove("count")

    # 列出所有 key
    keys = page.session.store.get_keys()

    # 清空
    page.session.store.clear()
```

### 自定義 Connection（結合桌面模式）

在桌面模式，`FletSocketServer` 是預設傳輸。桌面模式不使用 HTTP，而是直接建立 TCP/UDS socket 連線到 Flet 伺服器程序。

---

## 重要發現與注意事項

### 1. PubSub 是程序級廣播，不是分頁級

`PubSubHub` 在 `FletSocketServer.__init__` 中建立（第 76 行），是每個 Flet 程序只有一個的單例。多個分頁/視窗連到同一程序時，PubSub 可以跨視窗通訊。

### 2. Session 關閉時自動清理 PubSub 訂閱

`Session.close()` 會呼叫 `pubsub_client.unsubscribe_all()`，不需要手動在 finally 區塊清理。

### 3. 斷線期間的訊息處理策略

- `Session.__send_buffer` 只在「session 存在但尚未設定 `__conn`」（非常短暫的視窗）保留訊息
- 一旦 `disconnect()` 設定了 `expires_at`，斷線期間的**增量流量直接丢棄**（第 383-384 行 comment：「Drop incremental traffic to avoid unbounded buffering」）
- 這意味著：斷線時的 UI 更新不會累積到重連後

### 4. invoke_method 是雙向的，透過 call_id 關聯

`Session.invoke_method()` 建立一個 `asyncio.Event`，以 `call_id` 為 key 存入 `__method_calls`。當 client 回應 `INVOKE_METHOD` 時，由 `handle_invoke_method_results()` 找到對應 Event 並設定。

超時會引發 `TimeoutError`，並從 `__method_calls` 中移除該 entry。

### 5. invoke_method 差異：桌面 vs 瀏覽器

- 瀏覽器模式：需要 client 實現方法並回傳
- 桌面模式：同樣走同一個 WebSocket 連線，行為一致

### 6. Session 和 Connection 的區分

- **Connection**（`FletSocketServer`）：傳輸層，代表一個活躍的 socket 連線
- **Session**（`Session`）：邏輯層，綁定一個 `Connection`，擁有自己的 Page、Control Index、PubSubClient
- 一個 Connection 同時只有一個 Session，但可以反覆連線/斷線（reconnect）

### 7. 弱引用索引防止記憶體洩漏

`Session.__index` 是 `WeakValueDictionary`，控制項實例沒有其他地方引用時會被自動回收，不需手動管理。

### 8. 更新排程器（Updates Scheduler）

`Session.schedule_update()` 將控制項加入 `__pending_updates`，然後由 `__updates_scheduler()` 背景任務統一處理。這是為了批次（batch）處理多個 `update()` 呼叫，減少網路往返。

### 9. MessagePack ext type 4 是字串

`decode_ext_from_msgpack` 中 `code == 4` 回傳 `data.decode("utf-8")`，這讓時間相關的 ISO 字串能正確傳遞。

### 10. SessionStore 是程序記憶體，不是持久化儲存

註解明确說明：「data stored in a session store is transient and is not preserved between app restarts.」

---

## 檔案行號索引

| 檔案 | 重點行號 |
|------|---------|
| `pubsub_hub.py` | 24-35（資料結構）、112-139（subscribe_topic）、189-212（__send）、149-188（各 send_* 方法） |
| `pubsub_client.py` | 全文，類別本身就是 API 集合 |
| `connection.py` | 28-35（pubsubhub property）、68-77（send_message 抽象方法） |
| `protocol.py` | 127-157（ClientAction）、159-185（ClientMessage）、187-317（各 Body dataclass） |
| `session.py` | 42（pubsub_client 建立）、93-99（pubsub_client property）、165-201（connect/disconnect/close）、203-280（各生命週期方法）、335-390（訊息發送與排程） |
| `session_store.py` | 全文，簡單的 dict wrapper |
| `flet_socket_server.py` | 88-113（傳輸選擇）、165-201（連線處理）、231-275（I/O 迴圈）、278-325（訊息分發） |
