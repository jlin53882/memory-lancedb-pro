# Venv 核心套件學習筆記

> 來源：Minecraft_translator_flet 專案 venv
> 版本資訊記錄於各套件章節
> 筆記重點：實際 API 用法與模型記憶可能不同的部分

---

## 1. Pydantic (v2.12.3)

### 模組結構
```
pydantic/
├── __init__.py          # 主入口，導出所有公開 API
├── main.py              # BaseModel, create_model
├── config.py            # ConfigDict, with_config
├── fields.py            # Field, FieldInfo, PrivateAttr, computed_field
├── types.py             # 各類型約束 (Strict, conint, conlist, EmailStr 等)
├── networks.py          # URL 相關類型 (HttpUrl, AnyUrl 等)
├── errors.py            # 錯誤類別
├── validators.py       # 驗證器裝飾器
├── root_model.py        # RootModel
├── type_adapter.py     # TypeAdapter
└── functional_validators.py  # field_validator, model_validator 等
```

### 主要 Class/Function 及其簽名

#### BaseModel (main.py)
```python
class BaseModel(metaclass=_model_construction.ModelMetaclass):
    """Pydantic 模型基類"""
    
    model_config: ClassVar[ConfigDict] = ConfigDict()
    """模型配置，應為字典"""
    
    # 主要方法
    def __init__(__pydantic_self__, **data: Any) -> None:
        """初始化模型，自動驗證"""
    
    @classmethod
    def model_validate(cls, obj: Any, ...) -> Self:
        """驗證並返回模型實例"""
    
    def model_dump(self, ...) -> dict[str, Any]:
        """導出為字典"""
    
    def model_dump_json(self, ...) -> str:
        """導出為 JSON 字串"""
    
    def model_json_schema(self, ...) -> dict[str, Any]:
        """生成 JSON Schema"""
    
    def model_copy(self, ...) -> Self:
        """淺/深拷貝"""
    
    @classmethod
    def model_validate_json(cls, json_bytes: str | bytes, ...) -> Self:
        """直接從 JSON 解析"""
```

#### Field (fields.py)
```python
def Field(
    default: Any = PydanticUndefined,
    *,
    default_factory: Callable[[], Any] | None = None,
    alias: str | None = None,
    alias_priority: int | None = None,
    validation_alias: str | AliasPath | AliasChoices | None = None,
    serialization_alias: str | None = None,
    title: str | None = None,
    description: str | None = None,
    examples: list[Any] | None = None,
    exclude: bool | None = None,
    gt: annotated_types.SupportsGt | None = None,
    ge: annotated_types.SupportsGe | None = None,
    lt: annotated_types.SupportsLt | None = None,
    le: annotated_types.SupportsLe | None = None,
    multiple_of: float | None = None,
    strict: bool | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | re.Pattern[str] | None = None,
    # ... 更多參數
) -> FieldInfo:
    """定義模型欄位"""
```

#### ConfigDict (config.py)
```python
class ConfigDict(TypedDict, total=False):
    """模型配置字典"""
    
    title: str | None
    """JSON Schema 標題"""
    
    model_title_generator: Callable[[type], str] | None
    """生成模型標題的函數"""
    
    extra: ExtraValues | None  # 'allow' | 'ignore' | 'forbid'
    """額外欄位處理策略"""
    
    frozen: bool  # 防止修改
    validate_assignment: bool  # 賦值時驗證
    str_to_lower: bool
    str_to_upper: bool
    str_strip_whitespace: bool
    # ... 更多配置
```

#### 驗證器裝飾器
```python
@field_validator('field_name', mode='before|after|wrap')
def validate_field(cls, v: Any) -> Any:
    """欄位驗證器"""

@model_validator(mode='before|after|wrap')
def validate_model(cls, data: Any) -> Any:
    """模型驗證器"""

@field_serializer('field_name')
def serialize_field(cls, v: Any) -> Any:
    """欄位序列化器"""

@computed_field
@property
def computed_property(self) -> Any:
    """計算屬性"""
```

### 重要 API 用法（與模型記憶可能不同的部分）

1. **v2 驗證模式改變**：
   - `model_validate` 取代 `parse_obj`
   - `model_dump` 取代 `dict()` 
   - `model_validate_json` 可直接解析 JSON 位元組

2. **Field 參數變化**：
   - `min_length`/`max_length` 取代 `min_items`/`max_items`（針對字串）
   - `gt`/`ge`/`lt`/`le` 取代 `ge`/`gt`/`le`/`lt`

3. **配置方式**：
   - 使用 `model_config = ConfigDict(...)` 而非 `class Config`
   - `Extra` 枚举改為 `extra: Literal['allow', 'ignore', 'forbid']`

4. **泛型模型**：
   ```python
   from typing import Generic, TypeVar
   
   T = TypeVar('T')
   
   class Container(BaseModel, Generic[T]):
       item: T
   ```

---

## 2. FastAPI (v0.119.1)

### 模組結構
```
fastapi/
├── __init__.py              # 導出主要 API
├── applications.py         # FastAPI 類
├── routing.py              # APIRouter
├── params.py               # 參數類定義
├── param_functions.py      # 依賴注入參數函數
├── requests.py             # Request 類
├── responses.py            # Response 類
├── exceptions.py           # HTTPException
├── dependencies/           # 依賴注入
├── middleware/             # 中間件
├── security/               # 安全相關
└── openapi/               # OpenAPI 生成
```

### 主要 Class/Function 及其簽名

#### FastAPI (applications.py)
```python
class FastAPI(Starlette):
    """
    FastAPI 應用程式主類
    """
    
    def __init__(
        self,
        debug: bool = False,
        routes: Optional[List[BaseRoute]] = None,
        title: str = "FastAPI",
        summary: Optional[str] = None,
        description: str = "",
        version: str = "0.1.0",
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc",
        # ... 更多參數
    ) -> None:
        """初始化 FastAPI 應用"""
    
    # HTTP 方法裝飾器
    @async_cache
    def get(self, path: str, ..., name: str | None = None) -> Callable[[T], T]:
        """GET 路由"""
    
    def post(self, path: str, ...) -> Callable[[T], T]:
        """POST 路由"""
    
    def put(self, path: str, ...) -> Callable[[T], T]:
        """PUT 路由"""
    
    def delete(self, path: str, ...) -> Callable[[T], T]:
        """DELETE 路由"""
    
    def patch(self, path: str, ...) -> Callable[[T], T]:
        """PATCH 路由"""
    
    # WebSocket
    def websocket(self, path: str, ...) -> Callable[[T], T]:
        """WebSocket 路由"""
```

#### APIRouter (routing.py)
```python
class APIRouter:
    """API 路由容器"""
    
    def __init__(
        self,
        prefix: str = "",
        tags: list[str | None] | None = None,
        dependencies: list[Depends] | None = None,
        default_response_class: type[Response] | None = None,
        # ... 更多參數
    ) -> None:
        """初始化路由器"""
    
    def get(self, path: str, ...) -> Callable[[T], T]:
        """GET 路由"""
    
    def post(self, path: str, ...) -> Callable[[T], T]:
        """POST 路由"""
    # ... 其他 HTTP 方法
```

#### 依賴注入參數函數 (param_functions.py)
```python
def Depends(dependency: Callable[..., Any] | None = None, *, use_cache: bool = True) -> Any:
    """依賴注入"""

def Body(..., embed: bool = False) -> Any:
    """請求體參數"""

def Query(..., default: Any = Undefined) -> Any:
    """URL 查詢參數"""

def Path(..., default: Any = Undefined) -> Any:
    """路徑參數"""

def Header(..., default: Any = Undefined, convert_underscores: bool = True) -> Any:
    """HTTP Header 參數"""

def Cookie(..., default: Any = Undefined) -> Any:
    """Cookie 參數"""

def Form(..., default: Any = Undefined) -> Any:
    """表單資料"""

def File(..., default: Any = Undefined) -> Any:
    """上傳檔案"""

def Security(dependency: Callable[..., Any] | None = None, ...) -> Any:
    """安全依賴（支援 OAuth2）"""
```

### 重要 API 用法

1. **路徑參數自動類型轉換**：
   ```python
   @app.get("/items/{item_id}")
   def read_item(item_id: int):
       return {"item_id": item_id}  # 自動轉為 int
   ```

2. **Response Model**：
   ```python
   @app.get("/users", response_model=list[User])
   def get_users():
       return users
   ```

3. **狀態碼**：
   ```python
   from fastapi import status
   
   @app.post("/items", status_code=status.HTTP_201_CREATED)
   def create_item(item: Item):
       return item
   ```

4. **錯誤處理**：
   ```python
   from fastapi import HTTPException
   
   @app.get("/items/{item_id}")
   def read_item(item_id: int):
       if item_id not in items:
           raise HTTPException(status_code=404, detail="Item not found")
       return items[item_id]
   ```

---

## 3. Uvicorn (v0.38.0)

### 模組結構
```
uvicorn/
├── __init__.py          # 導出 run, main, Config, Server
├── main.py              # CLI 入口，run() 函數
├── config.py            # Config 類
├── server.py            # Server 類
├── logging.py           # 日誌配置
├── workers.py           # 多進程 worker
├── importer.py          # 動態導入
├── lifespan/           # 生命週期管理
├── loops/               # 事件循環
├── middleware/          # 中間件
├── protocols/           # HTTP/WebSocket 協議
└── supervisors/         # 進程監督
```

### 主要 Class/Function 及其簽名

#### run() (main.py)
```python
def run(
    app: str | ASGIApplication,
    host: str = "127.0.0.1",
    port: int = 8000,
    uds: str | None = None,
    fd: int | None = None,
    reload: bool = False,
    reload_dirs: list[str] | None = None,
    reload_includes: list[str] | None = None,
    reload_excludes: list[str] | None = None,
    reload_delay: float = 0.25,
    workers: int | None = None,
    loop: LoopFactoryType = "auto",
    http: HTTPProtocolType = "auto",
    ws: WSProtocolType = "auto",
    ws_max_size: int = 16777216,
    ws_max_queue: int | None = None,
    ws_ping_interval: float | None = None,
    ws_ping_timeout: float | None = None,
    ws_per_message_deflate: bool = True,
    lifespan: LifespanType = "on",
    interface: InterfaceType = "asgi3",
    limit_concurrency: int | None = None,
    backlog: int = 2048,
    timeout_keep_alive: int = 5,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
    ssl_keyfile_password: str | None = None,
    ssl_version: int = ssl.PROTOCOL_TLS_SERVER,
    ssl_cert_reqs: int = ssl.CERT_REQUIRED,
    ssl_ciphers: str = "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256",
    ssl_ca_certs: str | None = None,
    ssl_ca_crl: str | None = None,
    ssl_ocsp_timeout: int = 5,
    use_colors: bool | None = None,
    app_dir: str | None = None,
    h11_max_incomplete_size: int = 16_384,
    h11_keep_alive: int = 5,
    ws_compression: str = "deflate",
    access_log: bool | None = None,
    use_subprocess: bool = False,
    loop_asyncio: bool = False,
    no_server: bool = False,
    headers: list[tuple[str, str]] | None = None,
    factory: bool = False,
    uds_perms: int | None = None,
    return_asyncio_server: bool = False,
    asyncio_server_factory: Callable[..., asyncio.AbstractServer] | None = None,
    **kwargs: Any,
) -> None:
    """執行 uvicorn 伺服器"""
```

#### Config (config.py)
```python
class Config:
    """伺服器配置類"""
    
    def __init__(
        self,
        app: str | ASGIApplication,
        host: str = "127.0.0.1",
        port: int = 8000,
        # ... 同 run() 參數
    ) -> None:
        """初始化配置"""
    
    @property
    def bind_socket(self) -> socket.socket:
        """綁定的 socket"""
```

#### Server (server.py)
```python
class Server:
    """UVicorn 伺服器"""
    
    def __init__(self, config: Config) -> None:
        """初始化伺服器"""
    
    @property
    def urls(self) -> list[str]:
        """伺服器 URL 列表"""
    
    async def serve(self) -> None:
        """啟動伺服器"""
    
    async def serve_single(self) -> None:
        """單次服務（測試用）"""
```

### 重要 API 用法

1. **ASGI 應用作為字串**：
   ```python
   # 方式 1: 字串路徑
   uvicorn.run("myapp:app")
   
   # 方式 2: 直接傳入 app 物件
   uvicorn.run(app)
   ```

2. **重載模式**：
   ```python
   uvicorn.run("myapp:app", reload=True, reload_dirs=["./app"])
   ```

3. **HTTPS**：
   ```python
   uvicorn.run(
       "myapp:app",
       ssl_keyfile="key.pem",
       ssl_certfile="cert.pem"
   )
   ```

4. **多 Worker**：
   ```python
   uvicorn.run("myapp:app", workers=4)
   ```

---

## 4. Google GenAI (google-generativeai) (v1.56.0)

### 模組結構
```
google/genai/
├── __init__.py          # 導出 Client
├── client.py            # Client 類（同步/非同步）
├── models.py            # 模型操作
├── types.py             # 類型定義（龐大，648KB+）
├── chats.py             # 對話 API
├── files.py             # 檔案管理
├── live.py              # 即時對話 API
├── operations.py        #長時間操作
├── tunings.py           # 模型微調
├── batches.py           # 批次處理
├── caches.py            # 快取管理
├── _api_client.py       # API 用戶端基礎類
└── _interactions.py     # 互動相關
```

### 主要 Class/Function 及其簽名

#### Client (client.py)
```python
class Client:
    """Google GenAI 客戶端"""
    
    def __init__(
        self,
        api_key: str | None = None,
        project: str | None = None,
        location: str | None = None,
        vertexai: bool = False,
        http_options: HttpOptions | HttpOptionsDict | None = None,
        # ... 更多參數
    ) -> None:
        """初始化客戶端"""
    
    @property
    def models(self) -> Models:
        """模型操作"""
    
    @property
    def chats(self) -> Chats:
        """對話操作"""
    
    @property
    def files(self) -> Files:
        """檔案操作"""
    
    @property
    def live(self) -> AsyncLive:
        """即時對話"""
    
    def close(self) -> None:
        """關閉客戶端"""
```

#### Models (models.py - 238KB+)
```python
class Models:
    """模型操作類"""
    
    def __init__(self, api_client: BaseApiClient):
        self._api_client = api_client
    
    def generate_content(
        self,
        model: str,
        contents: list[ContentType] | ContentType | None = None,
        config: GenerateContentConfig | None = None,
        *,
        stream: bool = False,
    ) -> GenerateContentResponse:
        """生成內容"""
    
    def count_tokens(
        self,
        model: str,
        contents: list[ContentType] | ContentType | None = None,
    ) -> CountTokensResponse:
        """計算 Token 數"""
    
    def embed_content(
        self,
        model: str,
        content: ContentType,
        task_type: str | None = None,
    ) -> EmbedContentResponse:
        """嵌入內容"""
```

#### Chats (chats.py)
```python
class Chats:
    """對話類"""
    
    def __init__(self, api_client: BaseApiClient):
        self._api_client = api_client
    
    @property
    def model(self) -> str:
        """當前模型"""
    
    @model.setter
    def model(self, value: str) -> None:
        """設定模型"""
    
    def send_message(
        self,
        message: str | list[PartType],
        *,
        config: GenerateContentConfig | None = None,
        stream: bool = False,
    ) -> GenerateContentResponse:
        """發送訊息"""
    
    def start_chat(
        self,
        history: list[ContentType] | None = None,
        tools: list[ToolType] | None = None,
        system_instruction: str | list[PartType] | None = None,
    ) -> ChatSession:
        """開始新對話"""
```

### 重要 API 用法

1. **基本使用**：
   ```python
   from google import genai
   
   client = genai.Client(api_key="YOUR_API_KEY")
   response = client.models.generate_content(
       model="gemini-2.0-flash",
       contents="Hello!"
   )
   print(response.text)
   ```

2. **對話模式**：
   ```python
   chat = client.chats.start_chat(
       model="gemini-2.0-flash",
       history=[{"role": "user", "parts": ["Hi"]}]
   )
   response = chat.send_message("Tell me a joke")
   print(response.text)
   ```

3. **串流回應**：
   ```python
   response = client.models.generate_content(
       model="gemini-2.0-flash",
       contents="Write a story",
       stream=True
   )
   for chunk in response:
       print(chunk.text)
   ```

4. **工具呼叫**：
   ```python
   from google.genai import types
   
   tools = [{"function_declarations": [...]}]
   response = client.models.generate_content(
       model="gemini-2.0-flash",
       contents="...",
       config=types.GenerateContentConfig(tools=tools)
   )
   ```

5. **Vertex AI**（企業版）：
   ```python
   client = genai.Client(
       project="my-project",
       location="us-central1",
       vertexai=True
   )
   ```

---

## 5. Requests (v2.32.5)

### 模組結構
```
requests/
├── __init__.py          # 導出主要 API
├── api.py               # 簡化 API (get, post 等)
├── sessions.py          # Session 類
├── models.py            # Request, Response, PreparedRequest
├── adapters.py          # HTTPAdapter
├── auth.py              # 認證類
├── cookies.py           # Cookie 處理
├── exceptions.py        # 異常類
├── hooks.py             # 鉤子
├── status_codes.py      # 狀態碼
├── structures.py        # 資料結構
├── utils.py             # 工具函數
└── compat.py            # 向後相容
```

### 主要 Class/Function 及其簽名

#### Session (sessions.py)
```python
class Session:
    """請求 Session"""
    
    def __init__(self) -> None:
        """初始化 Session"""
    
    def request(
        self,
        method: str,
        url: str,
        params: dict | list[tuple] | None = None,
        data: dict | str | bytes | None = None,
        json: dict | list[tuple] | None = None,
        headers: dict | None = None,
        cookies: dict | RequestsCookieJar | None = None,
        files: dict | None = None,
        auth: tuple[str, str] | Callable | None = None,
        timeout: float | tuple[float, float] | None = None,
        allow_redirects: bool = True,
        proxies: dict | None = None,
        verify: bool | str = True,
        stream: bool = False,
        cert: str | tuple[str, str] | None = None,
    ) -> Response:
        """發送請求"""
    
    def get(self, url: str, **kwargs) -> Response:
        """GET 請求"""
    
    def post(self, url: str, **kwargs) -> Response:
        """POST 請求"""
    
    def put(self, url: str, **kwargs) -> Response:
        """PUT 請求"""
    
    def delete(self, url: str, **kwargs) -> Response:
        """DELETE 請求"""
    
    def patch(self, url: str, **kwargs) -> Response:
        """PATCH 請求"""
    
    def head(self, url: str, **kwargs) -> Response:
        """HEAD 請求"""
    
    def options(self, url: str, **kwargs) -> Response:
        """OPTIONS 請求"""
    
    def close(self) -> None:
        """關閉 Session"""
```

#### Response (models.py)
```python
class Response:
    """HTTP 回應"""
    
    status_code: int
    """HTTP 狀態碼"""
    
    headers: CaseInsensitiveDict
    """回應頭"""
    
    content: bytes
    """回應主體（原始位元組）"""
    
    text: str
    """回應主體（解碼為文字）"""
    
    json(**kwargs)
    """將回應解析為 JSON"""
    
    @property
    def url(self) -> str:
        """最終 URL（考慮重定向）"""
    
    @property
    def is_redirect(self) -> bool:
        """是否為重定向"""
    
    @property
    def is_permanent_redirect(self) -> bool:
        """是否為永久重定向"""
    
    def raise_for_status(self) -> None:
        """若狀態碼表示錯誤則拋出異常"""
    
    def close(self) -> None:
        """關閉連接"""
```

### 重要 API 用法

1. **基本請求**：
   ```python
   import requests
   
   # GET
   r = requests.get('https://api.github.com/user')
   
   # POST
   r = requests.post('https://httpbin.org/post', data={'key': 'value'})
   
   # JSON POST
   r = requests.post('https://httpbin.org/post', json={'key': 'value'})
   ```

2. **帶認證**：
   ```python
   # Basic Auth
   r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
   
   # 或使用
   from requests.auth import HTTPBasicAuth
   r = requests.get('url', auth=HTTPBasicAuth('user', 'pass'))
   ```

3. **自訂 Headers**：
   ```python
   headers = {'User-Agent': 'my-app/1.0'}
   r = requests.get('https://api.github.com/user', headers=headers)
   ```

4. **Timeout**：
   ```python
   # 連接 timeout 和讀取 timeout
   r = requests.get('https://example.com', timeout=(5, 30))
   ```

5. **Session 使用**：
   ```python
   session = requests.Session()
   session.headers.update({'Authorization': 'Bearer token'})
   r = session.get('https://api.example.com/data')
   ```

6. **檔案上傳**：
   ```python
   files = {'file': open('report.pdf', 'rb')}
   r = requests.post('https://httpbin.org/post', files=files)
   ```

---

## 6. HTTPX (v0.28.1)

### 模組結構
```
httpx/
├── __init__.py          # 導出主要 API
├── _client.py           # Client, AsyncClient
├── _models.py          # Request, Response, Headers, Cookies
├── _config.py          # Timeout, Limits, Proxy 配置
├── _auth.py            # 認證類
├── _api.py             # 簡化 API (get, post 等)
├── _content.py         # 請求/回應內容處理
├── _decoders.py        # 解碼器
├── _exceptions.py      # 異常類
├── _types.py          # 類型定義
├── _urls.py           # URL 處理
├── _utils.py          # 工具函數
└── _transports/       # 傳輸層
```

### 主要 Class/Function 及其簽名

#### Client (_client.py)
```python
class Client:
    """同步 HTTP 客戶端"""
    
    def __init__(
        self,
        base_url: str | URL | None = None,
        auth: Auth | tuple[str, str] | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | Cookie | None = None,
        timeout: Timeout | float | None = None,
        limits: Limits | None = None,
        max_redirects: int = 20,
        event_hooks: dict[str, list[Callable]] | None = None,
        transport: BaseTransport | None = None,
        app: Callable | None = None,
        trust_env: bool = True,
        follow_redirects: bool = False,
        http1: bool = True,
        http2: bool = False,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
    ) -> None:
        """初始化客戶端"""
    
    def request(
        self,
        method: str,
        url: str | URL,
        content: bytes | str | None = None,
        data: dict | bytes | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | Cookie | None = None,
        auth: Auth | tuple[str, str] | None = None,
        timeout: Timeout | float | None = None,
        follow_redirects: bool | None = None,
        max_redirects: int | None = None,
        event_hooks: dict[str, list[Callable]] | None = None,
    ) -> Response:
        """發送請求"""
    
    def get(self, url: str | URL, **kwargs) -> Response:
        """GET 請求"""
    
    def post(self, url: str | URL, **kwargs) -> Response:
        """POST 請求"""
    
    # ... 其他 HTTP 方法
    
    def close(self) -> None:
        """關閉客戶端"""
    
    def __enter__(self) -> Client:
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
```

#### AsyncClient (_client.py)
```python
class AsyncClient:
    """非同步 HTTP 客戶端"""
    
    def __init__(self, ...):  # 參數與 Client 相同
    
    async def request(...) -> Response:
        """非同步發送請求"""
    
    async def get(self, url: str | URL, **kwargs) -> Response:
        """非同步 GET 請求"""
    
    async def post(self, url: str | URL, **kwargs) -> Response:
        """非同步 POST 請求"""
    
    # ... 其他 HTTP 方法
    
    async def aclose(self) -> None:
        """非同步關閉"""
```

#### Response (_models.py)
```python
class Response:
    """HTTP 回應"""
    
    status_code: int
    """HTTP 狀態碼"""
    
    headers: Headers
    """回應頭"""
    
    content: bytes
    """回應主體"""
    
    text: str
    """回應文字"""
    
    def json(self, **kwargs) -> Any:
        """解析 JSON"""
    
    @property
    def url(self) -> URL:
        """最終 URL"""
    
    @property
    def is_redirect(self) -> bool:
        """是否重定向"""
    
    def raise_for_status(self) -> None:
        """錯誤時拋出異常"""
    
    def close(self) -> None:
        """關閉連接"""
```

### 重要 API 用法

1. **同步請求**：
   ```python
   import httpx
   
   # 簡化 API
   r = httpx.get('https://example.com')
   
   # 使用 Client（推薦，更高效）
   with httpx.Client() as client:
       r = client.get('https://example.com')
       print(r.status_code)
   ```

2. **非同步請求**：
   ```python
   import httpx
   
   async with httpx.AsyncClient() as client:
       r = await client.get('https://example.com')
       print(r.status_code)
   ```

3. **請求配置**：
   ```python
   client = httpx.Client(
       base_url='https://api.example.com',
       params={'key': 'value'},
       headers={'Authorization': 'Bearer token'},
       timeout=httpx.Timeout(10.0)
   )
   ```

4. **JSON 處理**：
   ```python
   # POST JSON
   r = client.post('https://api.example.com', json={'key': 'value'})
   
   # 解析 JSON 回應
   data = r.json()
   ```

5. **檔案上傳**：
   ```python
   files = {'upload': open('file.txt', 'rb')}
   r = client.post('https://example.com/upload', files=files)
   ```

6. **串流請求**：
   ```python
   with httpx.stream('GET', 'https://example.com/large-file') as r:
       for chunk in r.iter_bytes():
           process(chunk)
   ```

7. **HTTP/2**：
   ```python
   client = httpx.Client(http2=True)
   ```

8. **與 ASGI 應用集成**：
   ```python
   # 用於測試
   from myapp import app
   
   with httpx.Client(transport=httpx.ASGITransport(app=app)) as client:
       r = client.get('/items/')
   ```

---

## 總結比較

| 特性 | requests | httpx |
|------|----------|-------|
| 同步/非同步 | 僅同步 | 兩者皆支援 |
| HTTP/2 | 不支援 | 支援 |
| 連接池 | 基本 | 高級配置 |
| 串流 | 基本 | 高級支援 |
| ASGI 測試 | 無 | ASGITransport |
| 類型提示 | 基本 | 完整 |
| Timeout 設置 | tuple | Timeout 類 |

---

*筆記完成於 2026-03-15*
