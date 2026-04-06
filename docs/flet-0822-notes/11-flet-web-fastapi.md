# flet_web FastAPI 整合 — 學習筆記

> Flet 版本：0.82.2
> 閱讀日期：2026-03-23
> 目標檔案：7 個 `flet_web` FastAPI 整合相關模組

---

## flet_web 的角色與使用時機

### 定位
`flet_web` 是 Flet 的 **web 部署模式**套件。當你要把 Flet 應用程式部署到網頁環境時（例如透過 FastAPI 托管，或作為 PWA），就會用到這組模組。

### 與桌面模式的根本差異

| 維度 | 桌面模式（`flet`） | Web 模式（`flet_web.fastapi`） |
|---|---|---|
| 入口 | `flet.app.start()` | `flet_web.fastapi.app()` |
| 連線方式 | 原生通訊端（platform-specific） | **WebSocket**（瀏覽器 ↔ 伺服器） |
| 傳輸協定 | 自訂 binary（udp/tcp） | **msgpack over WebSocket** |
| 靜態檔案 | 不需要 | 需要（`index.html`、manifest、字體等） |
| Session 管理 | 程序內 | **程序內記憶體**（伺服器重啟會消失） |
| 上傳/下載 | 不需要 | 需要（`FletUpload` + 簽名 URL） |
| OAuth | 不需要 | 需要（`FletOAuth` callback） |
| 部署形態 | 獨立視窗 | **嵌入現有 Web 伺服器（FastAPI）** |

### 使用時機
- 需要将 Flet 嵌入現有 FastAPI 應用
- 部署為 PWA（漸進式網頁應用）
- 需要透過網頁瀏覽器存取 Flet UI
- 需要與其他 FastAPI 路由共存

---

## FletApp / FletFastAPI 類

### 架構總覽

```
FastAPI app
│
├── WebSocket 處理：/ws（預設）
│   └── FletApp.handle()
│       ├── __receive_loop()    — 接收 client 訊息
│       └── __send_loop()       — 傳送 server 訊息
│
├── Upload 處理：/upload（可自訂）
│   └── FletUpload.handle()
│
├── OAuth callback：/oauth_callback
│   └── FletOAuth.handle()
│
└── 靜態檔案：/（mount FletStaticFiles）
    └── FletStaticFiles（包含 index.html、manifest、assets）
```

### `flet_fastapi.py` — `FastAPI` 類（行 1-100）

```python
class FastAPI(fastapi.FastAPI):  # 行 34
```

這是對 `fastapi.FastAPI` 的**包裝類**，核心功能是透過 `lifespan` 上下文管理器整合 `app_manager` 的生命週期。

**重要機制 — lifespan（行 93-112）：**
```python
@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    await flet_web.fastapi.app_manager.start()   # 啟動時
    # ... user on_startup hooks ...
    yield
    # ... user on_shutdown hooks ...
    await flet_web.fastapi.app_manager.shutdown()  # 關閉時
```

**行 37-100**：幾乎所有參數都直接傳給底層 `fastapi.FastAPI`，代表這個包裝只疊加了 Flet 生命週期管理，並未改變原本 FastAPI 的任何行為。

---

### `flet_app.py` — `FletApp` 類（行 1-280）

```python
class FletApp(Connection):  # 行 67
```

`FletApp` 繼承自 `flet.messaging.connection.Connection`，是 **WebSocket 連線的核心處理器**。

#### `handle()` — WebSocket 處理入口（行 85-107）

```python
async def handle(self, websocket: WebSocket):  # 行 85
    await self.__websocket.accept()
    self.__send_queue = asyncio.Queue()
    send_loop_task = asyncio.create_task(self.__send_loop())
    await self.__receive_loop()
    await send_loop_task
    # disconnect 後，進入 session timeout 倒數
    await app_manager.disconnect_session(
        self.__get_unique_session_id(self.__session.id),
        self.__session_timeout_seconds,
    )
```

關鍵設計：
- **雙迴圈架構**：`__receive_loop()`（接收）+ `__send_loop()`（發送），透過 `asyncio.Queue` 串聯
- 連線斷開後**不立即刪除 session**，而是設定 `session_timeout_seconds`（預設 3600 秒）後才回收

#### `__on_message()` — 訊息分派（行 165-258）

依 `ClientAction` 類型分派：

| ClientAction | 處理方式 | 程式碼位置 |
|---|---|---|
| `REGISTER_CLIENT` | 建立/恢復 session，執行 `main` | 行 181-246 |
| `CONTROL_EVENT` | `asyncio.create_task` 分派到 control handler | 行 248-250 |
| `UPDATE_CONTROL_PROPS` | 直接 apply 到 session | 行 252-254 |
| `INVOKE_METHOD` | 處理 method 呼叫結果 | 行 256-258 |

**REGISTER_CLIENT 流程（行 181-246）：**
1. 嘗試用 `session_id` 找回現有 session（支援重連）
2. 檢查 OAuth state cookie（行 195-200）
3. 若無 session → 建立新 session → 執行 `before_main` → 執行 `main`
4. 若有 session → `reconnect_session` + 觸發 `route_change` 事件

#### `__on_session_created()` — 執行 main 函式（行 109-148）

支援四種 `main` 形態：

```python
if inspect.iscoroutinefunction(self.__main):      # async def
    await self.__main(self.__session.page)
elif inspect.isasyncgenfunction(self.__main):     # async generator
    async for _ in self.__main(self.__session.page):
        await self.__session.after_event(self.__session.page)
elif inspect.isgeneratorfunction(self.__main):   # sync generator
    for _ in self.__main(self.__session.page):
        await self.__session.after_event(self.__session.page)
else:                                              # sync def
    self.__main(self.__session.page)
```

#### Session ID 唯一性（行 274-289）

```python
def __get_unique_session_id(self, session_id: str):
    ip = self.__client_ip
    if ip in ["127.0.0.1", "::1"]:
        ip = ""  # localhost 忽略 IP
    client_hash = sha1(f"{ip}{self.__client_user_agent}")
    return f"{self.page_name}_{session_id}_{client_hash}"
```

**重要**：同一個 `session_id` 從不同 IP/UA 連線，會被视为不同 session。

---

### `flet_app_manager.py` — `FletAppManager` 類（行 1-170）

```python
app_manager = FletAppManager()  # 行 170（singleton 實例）
```

#### Session 管理（行 107-145）

```python
async def add_session(session_id, session)       # 行 121-130
async def get_session(session_id) -> Optional[Session]  # 行 107-117
async def reconnect_session(session_id, conn)     # 行 131-156
async def disconnect_session(session_id, timeout) # 行 157-168
async def delete_session(session_id)               # 行 145-153
```

**disconnect vs delete 的區別：**
- `disconnect_session`：設定 session 的 `expires_at`，不會立即刪除
- `delete_session`：從 `__sessions` 字典移除並呼叫 `session.close()`

#### 自動清理任務（行 171-189）

每 10 秒檢查一次：
```python
async def __evict_expired_sessions(self):    # 行 171-183
    while True:
        await asyncio.sleep(10)
        for session_id, session in self.__sessions.items():
            if datetime.now(timezone.utc) > session.expires_at:
                session_ids.append(session_id)
        for session_id in session_ids:
            await self.delete_session(session_id)
```

#### OAuth State 管理（行 154-170）

- `store_state(state_id, OAuthState)` — 儲存
- `retrieve_state(state_id) -> OAuthState` — 取回並**刪除**（一次性）

#### PubSubHub 快取（行 59-76）

每個 `main` handler（以函式物件為 key）共享一個 `PubSubHub`：
```python
def get_pubsubhub(self, session_handler, loop=None):
    psh = self.__pubsubhubs.get(session_handler, None)
    if psh is None:
        psh = PubSubHub(loop=loop, executor=self.__executor)
        self.__pubsubhubs[session_handler] = psh
    return psh
```

#### ThreadPoolExecutor（行 47-51）

```python
self.__executor = ThreadPoolExecutor(thread_name_prefix="flet_fastapi")
```

用於執行阻塞性工作，共享給所有 `PubSubHub` 實例。

---

## Static Files 處理

### `flet_static_files.py` — `FletStaticFiles` 類（行 1-120）

```python
class FletStaticFiles(StaticFiles):  # 行 57
```

#### 職責

1. 將 `index.html`、`manifest.json`、`FontManifest.json` **複製到暫存目錄**
2. 在暫存副本上**置換變數**（行 72-90）：
   - `base_href` — 部署路徑前綴
   - `websocket_endpoint_path` — WebSocket 路由
   - `app_name`、`app_description` — PWA 中繼資料
   - `web_renderer` — 渲染器類型（Auto/WebAssembly/WebGL）
   - `route_url_strategy` — 路由策略（path 或 hash）
   - `no_cdn` — 是否從 CDN 載入 CanvasKit/Pyodide

3. **`lookup_path()`**（行 68-78）：若找不到檔案，**回傳 `index.html`**（SPA fallback 機制）

#### 關鍵流程

```python
async def __call__(self, scope, receive, send):
    await self.__once.do(self.__config, scope["root_path"])  # 只執行一次
    await super().__call__(scope, receive, send)

def lookup_path(self, path: str):
    full_path, stat_result = super().lookup_path(path)
    if stat_result is None:
        return super().lookup_path(self.index[0])  # fallback to index.html
    return full_path, stat_result
```

#### `__config()` 初始化（行 80-120）

- 建立暫存目錄：`tempfile.mkdtemp()`（行 89）
- 複製並修補 `index.html`：`patch_index_html()`（行 103-110）
- 複製並修補 `manifest.json`：`patch_manifest_json()`（行 112-116）
- `self.all_directories` 追加順序：`[temp_dir, assets_dir, web_dir]`

#### MIME 類型修正（行 16-17）

```python
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("application/wasm", ".wasm")
```
Windows 預設不註冊這些類型，需手動新增。

---

## 上傳機制

### `uploads.py` — 簽名 URL 產生器（行 1-90）

#### 核心：`build_upload_url()`（行 15-32）

```python
def build_upload_url(upload_endpoint_path, file_name, expires_in_seconds, secret_key):
    expire_date = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
    query_string = build_upload_query_string(file_name, expire_date)
    signature = get_upload_signature(upload_endpoint_path, query_string, expire_date, secret_key)
    return f"/{upload_endpoint_path.strip('/')}?{query_string}&s={signature}"
```

**URL 格式：**
```
/upload?f=filename.txt&e=2026-03-23T10:00:00+00:00&s=<hmac_hex_signature>
```

#### 簽名機制：`get_upload_signature()`（行 62-90）

```python
# 第一步：從 secret_key + expire_date 衍生 signing_key
signing_key = hmac.new(
    secret_key.encode("utf-8"),
    expire_date.isoformat().encode("utf-8"),
    hashlib.sha256,
).digest()

# 第二步：用 signing_key 簽名 endpoint + query_string
signature = hmac.new(
    signing_key,
    f"{upload_endpoint_path.strip('/')}{query_string}".encode(),
    hashlib.sha256,
).hexdigest()
```

這是 **HMAC-based key derivation**：每次簽名都用不同的 `signing_key`（因為 `expire_date` 包含在 key derivation 中），避免 secret_key 直接暴露在網路上。

### `flet_app.py` — 上傳 URL 產生（行 260-277）

```python
def get_upload_url(self, file_name: str, expires: int) -> str:
    if not self.__upload_endpoint_path:
        raise RuntimeError("upload_path should be specified to enable uploads")
    return build_upload_url(
        self.__upload_endpoint_path,
        file_name,
        expires,
        self.__secret_key,
    )
```

由 `FletApp`（伺服器端）呼叫，產生**相對路徑的簽名 URL** 傳給 client，client 再拿這個 URL 去做 `PUT` 請求上傳。

---

## 常用程式碼範例（部署到 web）

### 基本部署（FastAPI）

```python
import flet_web.fastapi as flet_fastapi

def main(page: flet.Page):
    page.add(flet.Text("Hello, web!"))

# 建立 FastAPI app（已包含所有 Flet 路由）
app = flet_fastapi.app(
    main=main,
    assets_dir="C:/path/to/assets",
    app_name="My Flet App",
    app_short_name="FletApp",
    route_url_strategy="path",        # 或 "hash"
    web_renderer="auto",              # auto / webassembly / webgl
    no_cdn=False,                     # True = 使用本地 Pyodide/CanvasKit
    upload_dir="C:/path/to/uploads",
    max_upload_size=10 * 1024 * 1024,  # 10MB
    secret_key="your-secret-key",
)

# === 等同於手動建立（展示內部結構）===
# fastapi_app = FastAPI()
# fastapi_app.websocket("/ws")(app_handler)
# fastapi_app.mount("/", FletStaticFiles(...))
```

### OAuth 流程（完整）

```python
# OAuth 起始（你的 main 函式內）
async def main(page: flet.Page):
    def on_login(e):
        print(f"User logged in: {page.auth.user}")
    page.auth.on_user = on_login
    await page.login_oauth2(
        provider="google",
        redirect_url="https://yourapp.com/oauth_callback",
    )

app = flet_fastapi.app(
    main=main,
    secret_key="secret",
    oauth_state_timeout_seconds=600,  # 10 分鐘內必須完成 OAuth
)
```

### 與現有 FastAPI 路由共存

```python
import flet_fastapi as ff

flet_app = ff.app(main=main)

# 在另一個 FastAPI app 中 include
from fastapi import FastAPI
main_app = FastAPI()
main_app.mount("/flet", flet_app)  # /flet/* 所有 Flet 路由

# 新增你自己的 API 路由
@main_app.get("/api/health")
def health():
    return {"status": "ok"}
```

### 環境變數對照

| 環境變數 | 對應參數 | 說明 |
|---|---|---|
| `FLET_WEB_PATH` | — | Web 資產根目錄（預設用套件內建） |
| `FLET_WEB_RENDERER` | `web_renderer` | 覆寫 web renderer |
| `FLET_WEB_ROUTE_URL_STRATEGY` | `route_url_strategy` | 覆寫路由策略 |
| `FLET_WEB_NO_CDN` | `no_cdn` | 禁用 CDN |
| `FLET_SESSION_TIMEOUT` | `session_timeout_seconds` | Session 過期時間 |
| `FLET_OAUTH_STATE_TIMEOUT` | `oauth_state_timeout_seconds` | OAuth state 過期時間 |
| `FLET_UPLOAD_DIR` | `upload_dir` | 上傳檔案儲存目錄 |
| `FLET_SECRET_KEY` | `secret_key` | 上傳簽名密鑰 |
| `FLET_WEBSOCKET_HANDLER_ENDPOINT` | — | WebSocket endpoint 路徑 |
| `FLET_UPLOAD_HANDLER_ENDPOINT` | — | 上傳 endpoint 路徑 |
| `FLET_OAUTH_CALLBACK_HANDLER_ENDPOINT` | — | OAuth callback 路徑 |

### 上傳檔案流程（client 視角）

```python
# 1. 向 FletApp 取得簽名 URL
url = page.get_upload_url("report.pdf", expires=3600)

# 2. Client 用這個 URL 發 PUT 請求上傳
import httpx
with open("report.pdf", "rb") as f:
    await httpx.AsyncClient().put(url, content=f.read())
```

---

## 重要發現與注意事項

### 1. Session 記憶體限制
Session 全部存在 `FletAppManager.__sessions` 字典中（記憶體）。**伺服器重啟後所有 session 消失**，瀏覽器需要重新連線。這與桌面模式中程序結束即釋放不同，web 模式下需要自行處理 session 持久化需求。

### 2. WebSocket 雙迴圈設計
`__receive_loop()` 和 `__send_loop()` 是**完全獨立的兩個 asyncio 任務**，透過 `Queue` 溝通。當 `receive_loop` 發生錯誤，會送 `None` 給 `send_loop` 讓它優雅退出（行 139-141）。

### 3. index.html 動態修補
`FletStaticFiles.__config()` 會在**每次伺服器啟動時**建立新的暫存目錄並寫入修補後的 `index.html`。這代表：
- `index.html` 內容是**動態生成**的（根據傳入參數）
- 無法直接修改 `index.html` 來客製化——需要透過 `app()` 的參數或 `patch_index_html()` 等內部 API

### 4. HMAC 雙層簽名
上傳 URL 的簽名機制使用雙層 HMAC（行 67-90 of `uploads.py`）：先用 `secret_key + expire_date` 衍生 `signing_key`，再用 `signing_key` 簽名完整 URL。這樣即使 `secret_key` 洩漏，攻擊者也無法生成新過期時間的簽名（因為 `signing_key` 包含 `expire_date`）。

### 5. Security Headers 中間層（行 122-136 of `app.py`）
```python
response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
response.headers["Access-Control-Allow-Origin"] = "*"
```
這些是 Flet web runtime 正常運作**必要**的 headers（SharedArrayBuffer 需要 COOP/COEP）。若在 Flet app 外面再包一層 proxy，需確保這些 headers 不被移除。

### 6. 路由 fallback 機制
`FletStaticFiles.lookup_path()`（行 68-78）當找不到檔案時自動回傳 `index.html`。這是 SPA 路由的標準做法，讓 `route_change` 等事件由 JavaScript client 處理，而不是由伺服器處理。

### 7. OAuth state 是一次性的
`retrieve_state()`（行 159）在取出 OAuth state 的同時會**刪除**它（`pop`）。這防止了 replay attack。過期 state 由 `__evict_expired_oauth_states()` 每 10 秒清理。

### 8. `proxy_path` 的作用
`proxy_path` 用於反向代理情境（如 Nginx）。當 Flet app 不是掛在根路徑 `/` 而是 `/myapp/` 時，`proxy_path="/myapp"` 會讓所有內部連結和 WebSocket URL 都加上前綴。`FletStaticFiles` 會據此計算 `base_href`。

### 9. localhost 忽略 IP
在 `__get_unique_session_id()` 中（行 274-289），`127.0.0.1` 和 `::1` 會被忽略（設為空字串）。這是因為 localhost 使用者可能會更換網路介面，導致 IP 變動而不希望被視為不同 session。

### 10. ThreadPoolExecutor 共享
`FletAppManager.__executor` 是所有 session 和 pub/sub hub 共享的執行緒池。預設 `thread_name_prefix="flet_fastapi"`，適用於IO密集型操作。

---

## 模組對照總表

| 檔案 | 類別/函式 | 行數 | 職責 |
|---|---|---|---|
| `__init__.py` | `get_package_web_dir()` | 1-24 | 取 web 資產路徑 |
| `app.py` | `app()` | 1-137 | 高階 API：一次 mount 所有路由 |
| `flet_fastapi.py` | `FastAPI` | 1-100 | 包裝 FastAPI + lifespan 整合 |
| `flet_app.py` | `FletApp` | 1-290 | WebSocket 訊息處理 + session |
| `flet_app_manager.py` | `FletAppManager` | 1-170 | Session/OAuth state/PubSubHub 管理 |
| `flet_static_files.py` | `FletStaticFiles` | 1-120 | 靜態檔案服務 + index.html 修補 |
| `uploads.py` | `build_upload_url()` 等 | 1-90 | HMAC 簽名上傳 URL 產生 |
