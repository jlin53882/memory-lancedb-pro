# venv 套件學習筆記

> 來源：Minecraft_translator_flet venv  
> 路徑：`C:\Users\admin\Desktop\minecraft_translator_flet\.venv\Lib\site-packages`  
> 日期：2026-03-15

---

## 1. pytest (v9.0.2)

### 模組結構
pytest 是 Python 最流行的單元測試框架，核心模組位於 `pytest/` 目錄，主要從 `_pytest` 子模組匯出 API。

### 主要 API

#### 裝飾器與標記 (Marks)
```python
@pytest.fixture(scope="function", params=None, autouse=False)
# 用於定義測試 fixtures，scope 可選：function/class/module/package/session

@pytest.mark.parametrize("arg1", [val1, val2])
# 參數化測試

@pytest.mark.skip(reason="...")
@pytest.mark.skipif(condition, reason="...")
# 跳過測試

@pytest.mark.xfail(strict=False, reason="...")
# 預期失敗的測試
```

#### 斷言與例外
```python
pytest.raises(expected_exception, match=None)
# 斷言程式碼會引發指定異常

pytest.warns(expected_warning)
# 斷言程式碼會發出指定警告

pytest.approx(expected, rel=None, abs=None, nan_ok=False)
# 用於浮點數近等比較
```

#### 鉤子與配置
```python
pytest.fixture(autouse=False)  # 自動使用的 fixture
pytest.hookimpl(hookwrapper=False, tryfirst=False, pluggy=True)  # 插件實現
pytest.hookspec()  # 鉤子規範
```

#### 常用類別
```python
pytest.Config          # 測試配置對象
pytest.Session         # 測試會話根節點
pytest.Module          # 測試模組
pytest.Class           # 測試類別
pytest.Function        # 測試函數
pytest.ExceptionInfo  # 異常資訊封裝
pytest.MonkeyPatch    # 動態修改對象
pytest.TempPathFactory # 臨時目錄工廠
```

---

## 2. tqdm (v4.67.1)

### 模組結構
```
tqdm/
├── __init__.py       # 主入口，匯出 tqdm, trange
├── std.py            # 核心 tqdm 類別實作
├── cli.py            # 命令列介面
├── gui.py            # GUI 進度條
├── notebook.py       # Jupyter Notebook 支援
├── auto.py           # 自動選擇後端
├── asyncio.py         # asyncio 支援
└── contrib/          # 額外模組 (discord, slack, telegram, etc.)
```

### 主要類別與函數

#### tqdm 主類別
```python
class tqdm(Comparable):
    def __init__(
        self,
        iterable=None,      # 要裝飾的可迭代對象
        desc=None,          # 進度條描述前綴
        total=None,         # 總迭代次數
        leave=True,         # 結束後是否保留進度條
        file=None,          # 輸出目標 (預設 stderr)
        ncols=None,         # 進度條寬度
        mininterval=0.1,    # 最小更新間隔 (秒)
        maxinterval=10.0,   # 最大更新間隔 (秒)
        miniters=1,         # 最小更新次數
        unit='it',          # 計數單位
        unit_scale=False,   # 是否自動縮放
        unit_divisor=1000, # 數值除數
        dynamic_ncols=False,# 動態調整寬度
        smoothing=0.3,      # 平滑因子
        initial=0,          # 初始值
        position=None,      # 多列位置
        postfix=None,       # 附加字典
        **kwargs
    ):
```

#### 實用方法
```python
tqdm.update(n=1)          # 更新進度 n 步
tqdm.set_description(desc) # 設定描述
tqdm.set_postfix(**kwargs) # 設定附加資訊
tqdm.set_postfix_str(s)    # 設定字串附加資訊
tqdm.close()               # 關閉進度條
tqdm.clear()              # 清除顯示
tqdm.refresh()            # 強制刷新顯示
```

#### 便捷函數
```python
trange(*args, **kwargs)   # 等同於 tqdm(range(*args), **kwargs)

# 特殊版本
tqdm.notebook.tqdm        # Jupyter Notebook 版本
tqdm.gui.tqdm             # GUI 版本
tqdm.asyncio.tqdm         # Async 版本
```

---

## 3. watchdog (v4.0.2)

### 模組結構
```
watchdog/
├── __init__.py           # 主入口
├── events.py             # 事件類別與處理器
├── observers/             # 平台特定觀察者實現
│   ├── api.py           # 觀察者抽象基類
│   ├── polling.py       # 輪詢觀察者
│   ├── inotify.py       # Linux inotify
│   ├── fsevents.py      # macOS FSEvents
│   └── read_directory_changes.py  # Windows
└── utils/                 # 工具函數
    ├── patterns.py       # 模式匹配
    └── dirsnapshot.py   # 目錄快照
```

### 主要類別

#### 事件類別 (watchdog.events)
```python
# 事件類型常數
EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"
EVENT_TYPE_CLOSED = "closed"
EVENT_TYPE_OPENED = "opened"

# 檔案系統事件
class FileSystemEvent:
    src_path: str
    dest_path: str
    event_type: str
    is_directory: bool
    is_synthetic: bool

# 具體事件子類別
class FileCreatedEvent(FileSystemEvent)
class FileModifiedEvent(FileSystemEvent)
class FileDeletedEvent(FileSystemEvent)
class FileMovedEvent(FileSystemEvent)
class FileClosedEvent(FileSystemEvent)
class FileOpenedEvent(FileSystemEvent)
class DirCreatedEvent(FileSystemEvent)
class DirModifiedEvent(FileSystemEvent)
class DirDeletedEvent(FileSystemEvent)
class DirMovedEvent(FileSystemEvent)
```

#### 事件處理器
```python
class FileSystemEventHandler:
    def on_any_event(event)      # 任何事件發生時
    def on_created(event)        # 檔案/目錄創建
    def on_modified(event)       # 檔案/目錄修改
    def on_deleted(event)        # 檔案/目錄刪除
    def on_moved(event)          # 檔案/目錄移動

class PatternMatchingEventHandler(FileSystemEventHandler):
    def __init__(self, patterns=None, ignore_patterns=None, ignore_directories=False)

class RegexMatchingEventHandler(FileSystemEventHandler)
class LoggingEventHandler(FileSystemEventHandler)  # 內建日誌處理器
```

#### 觀察者 (observers)
```python
class Observer:
    def __init__(self, timeout=1)                    # 構造函數
    def schedule(event_handler, path, recursive)    # 排程監控
    def start()                                      # 啟動觀察者執行緒
    def stop()                                       # 停止觀察者
    def join(timeout=None)                          # 等待執行緒結束
    def add_handler_for_watch(handler, watch)        # 為 watch 新增處理器
    def remove_handler_for_watch(handler, watch)     # 移除處理器

# 使用範例
observer = Observer()
observer.schedule(MyEventHandler(), path, recursive=True)
observer.start()
# ... 處理事件 ...
observer.stop()
```

---

## 4. websockets (v15.0.1)

### 模組結構
```
websockets/
├── __init__.py           # 主入口，lazy import
├── client.py             # Sans-I/O 客戶端協議
├── server.py             # Sans-I/O 服務器協議
├── protocol.py           # 基礎協議實現
├── connection.py         # 連接抽象基類
├── frames.py             # WebSocket 幀處理
├── headers.py           # HTTP 標頭解析/構建
├── exceptions.py         # 異常類別
├── datastructures.py    # 資料結構
├── uri.py                # URI 解析
├── asyncio/              # asyncio 實現
│   ├── client.py        # async 客戶端
│   ├── server.py        # async 服務器
│   └── connection.py    # async 連接
├── sync/                 # 同步實現
└── legacy/               # 舊版相容實現 (已廢棄)
```

### 主要 API

#### Asyncio 客戶端
```python
async connect(
    uri: str,
    *,
    # 連接選項
    ssl=None,
    ping_interval=20,
    ping_timeout=20,
    close_timeout=10,
    max_size=2**20,
    
    # 協議選項
    extensions=None,
    subprotocols=None,
    
    # 額外選項
    additional_headers=None,
    user_agent_header="websockets/15.0.1",
    proxy=None,
    extra_headers=None,
) -> ClientConnection
```

#### Asyncio 服務器
```python
async serve(
    handler: Callable,
    host=None,
    port=None,
    *,
    # 協議選項
    ssl=None,
    ping_interval=20,
    ping_timeout=20,
    close_timeout=10,
    max_size=2**20,
    
    # 服務器選項
    origins=None,
    extensions=None,
    subprotocols=None,
    process_request=None,
    select_subprotocol=None,
) -> Server
```

#### 連接對象 (ClientConnection / ServerConnection)
```python
class ClientConnection:
    async def recv() -> str | bytes           # 接收訊息
    async def send(message)                   # 發送訊息
    async def close(code=1000, reason="")     # 關閉連接
    async def ping(data=None)                 # 發送 ping
    async def pong(data=None)                 # 發送 pong
    
    # 屬性
    state: State                              # 連接狀態
    subprotocol: str | None                    # 協商的子協議
    response: Response                         # HTTP 響應

# 異步迭代接收訊息
async for message in websocket:
    await process(message)
```

#### 例外類別
```python
WebSocketException           # 基類
ConnectionClosed            # 連接已關閉
ConnectionClosedOK          # 正常關閉 (1000)
ConnectionClosedError       # 異常關閉
InvalidURI                  # 無效 URI
InvalidHandshake            # 無效握手
InvalidStatus               # 無效狀態碼
PayloadTooBig               # 負載過大
NegotiationError            # 協商失敗
SecurityError               # 安全錯誤
```

---

## 5. qrcode (v7.4.2)

### 模組結構
```
qrcode/
├── __init__.py           # 主入口
├── main.py               # QRCode 類別
├── util.py               # 工具函數
├── base.py               # 基礎實現
├── constants.py          # 常數定義
├── exceptions.py         # 異常類別
├── image/                # 圖像生成器
│   ├── base.py          # 基礎圖像接口
│   ├── pil.py           # PIL/Pillow 圖像
│   ├── svg.py           # SVG 圖像
│   └── styledpil.py    # 樣式化 PIL 圖像
└── compat/               # 相容層
```

### 主要 API

#### QRCode 類別
```python
class QRCode(Generic[GenericImage]):
    def __init__(
        self,
        version=None,                    # QR 碼版本 (1-40)，None 為自動
        error_correction=ERROR_CORRECT_M,  # 錯誤校正級別
        box_size=10,                     # 每個模組的像素大小
        border=4,                        # 邊框寬度（模組數）
        image_factory=None,              # 圖像工廠類
        mask_pattern=None,               # 遮罩模式 (0-7)
    ):
    
    # 方法
    def add_data(self, data, optimize=20)  # 添加資料
    def make(self, image_factory=None)      # 生成 QR 碼數據
    def make_image(self, image_factory=None, fill_color=None, back_color=None)  # 生成圖像
    
    # 屬性
    modules: List[List[bool]]              # QR 碼模組矩陣
    version: int                           # QR 碼版本
    error_correction_level: int           # 錯誤校正級別
    mask_pattern: int                      # 遮罩模式
```

#### 錯誤校正常數
```python
ERROR_CORRECT_L   # 7% 錯誤校正
ERROR_CORRECT_M   # 15% 錯誤校正 (預設)
ERROR_CORRECT_Q   # 25% 錯誤校正
ERROR_CORRECT_H   # 30% 錯誤校正
```

#### 便捷函數
```python
# 最簡單用法
import qrcode
img = qrcode.make("Hello World")
img.save("qr.png")

# 或使用 QRCode 類
qr = qrcode.QRCode()
qr.add_data("Hello World")
img = qr.make_image()
```

---

## 6. toml (v0.10.2)

### 模組結構
```
toml/
├── __init__.py           # 主入口
├── decoder.py            # 解碼器
├── encoder.py            # 編碼器
├── ordered.py            # 有序字典
└── tz.py                 # 時區處理
```

### 主要 API

#### 載入函數
```python
# 從檔案載入
toml.load(fp: IO[str]) -> dict

# 從字串載入
toml.loads(s: str) -> dict
```

#### 傾印函數
```python
# 傾印到檔案
toml.dump(obj: dict, fp: IO[str]) -> None

# 傾印到字串
toml.dumps(obj: dict) -> str
```

#### 異常類別
```python
class TomlDecodeError(ValueError):
    # 屬性
    msg: str
    doc: str
    pos: int
    lineno: int
    colno: int
```

#### 編碼器類別
```python
class TomlEncoder:
    def __init__(self, _dict: type = dict)
    def encode(self, obj) -> str
    def get_empty_table(self) -> dict
    def get_primitives(self, obj, parent: Any)
    def get_truncate_table(self) -> bool

class TomlPreserveCommentEncoder(TomlEncoder)  # 保留註釋
class TomlArraySeparatorEncoder(TomlEncoder)  # 自定義陣列分隔符
class TomlPreserveInlineDictEncoder(TomlEncoder)  # 保留行內字典
class TomlNumpyEncoder(TomlEncoder)          # NumPy 陣列支援
class TomlPathlibEncoder(TomlEncoder)        # pathlib.Path 支援
```

#### 解碼器類別
```python
class TomlDecoder:
    def load(self, s: str) -> dict

class TomlDecodeError(Exception)
class TomlPreserveCommentDecoder(TomlDecoder)
```

#### 使用範例
```python
import toml

# 解析 TOML
config = toml.loads("""
[server]
host = "localhost"
port = 8080

[database]
enabled = true
""")

# 編碼為 TOML
toml_string = toml.dumps({"server": {"host": "localhost", "port": 8080}})

# 檔案操作
with open("config.toml", "r") as f:
    config = toml.load(f)
```

---

## 總結

| 套件 | 版本 | 用途 |
|------|------|------|
| pytest | 9.0.2 | Python 單元測試框架 |
| tqdm | 4.67.1 | 進度條顯示 |
| watchdog | 4.0.2 | 檔案系統事件監控 |
| websockets | 15.0.1 | WebSocket 客戶端/服務器 |
| qrcode | 7.4.2 | QR 碼生成 |
| toml | 0.10.2 | TOML 檔案解析/生成 |
