# Venv 套件學習筆記 (misc)

> 來源：`C:\Users\admin\Desktop\minecraft_translator_flet\.venv\Lib\site-packages`
> 記錄日期：2026-03-15

---

## 1. rich - 終端美化庫

### 模組結構
- `rich/console.py` - 核心 Console 類
- `rich/progress.py` - 進度條
- `rich/table.py` - 表格輸出
- `rich/text.py` - 文本處理
- `rich/style.py` - 樣式定義
- `rich/panel.py` - 面板輸出

### 主要 API

```python
# 全域 Console
from rich import get_console, reconfigure, print, inspect, print_json

console = get_console()  # 取得全域 Console 實例

# 列印富文本
from rich.console import Console
console = Console()
console.print("[bold red]Hello[/bold red] World!")

# 進度條
from rich.progress import track, Progress, BarColumn, TextColumn
for item in track(sequence, description="Processing"):
    pass

# 表格
from rich.table import Table
table = Table(title="Heroes")
table.add_column("Name", style="cyan")
table.add_row("Alice", "Bob")

# JSON 輸出
from rich import print_json
print_json(data={"key": "value"})
```

### 關鍵類別
- `Console` - 主要輸出類別
- `Text` - 富文本对象
- `Style` - 樣式定义
- `Progress` - 進度條管理
- `Table` - 表格构建

---

## 2. click - 命令列介面框架

### 模組結構
- `click/core.py` - 核心類別 (Context, Command, Group, Option, Argument)
- `click/decorators.py` - 裝飾器 (@command, @option, @argument)
- `click/types.py` - 參數類型 (STRING, INT, FLOAT, Choice, Path, File)
- `click/exceptions.py` - 例外處理
- `click/termui.py` - 終端 UI (prompt, confirm, progressbar)

### 主要 API

```python
import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    for _ in range(count):
        click.echo(f'Hello, {name}!')

# 參數裝飾器
@click.argument('filename')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')

# 群組命令
@click.group()
def cli():
    pass

@cli.command()
def subcommand():
    pass

# 類型支援
@click.option('--choice', type=click.Choice(['a', 'b', 'c']))
@click.option('--path', type=click.Path(exists=True))
@click.option('--count', type=int, default=10)

# 終端互動
name = click.prompt('Enter your name', default='John')
if click.confirm('Do you want to continue?'):
    pass

# 獲取上下文
ctx = click.get_current_context()
```

### 關鍵類別
- `Command` - CLI 命令
- `Group` - 命令群組
- `Option` / `Argument` - 參數定義
- `Context` - 執行上下文
- `ParamType` - 參數類型基類

---

## 3. cookiecutter - 專案範本生成器

### 模組結構
- `cookiecutter/main.py` - 主入口 `cookiecutter()` 函數
- `cookiecutter/generate.py` - 檔案生成
- `cookiecutter/prompt.py` - 互動式提示
- `cookiecutter/hooks.py` - 鉤子執行
- `cookiecutter/repository.py` - 範本倉庫處理

### 主要 API

```python
from cookiecutter import cookiecutter

# 基本使用
cookiecutter(
    'https://github.com/user/repo.git',  # 範本路徑
    checkout='v1.0',                      # Git branch/tag
    no_input=False,                       # 是否互動式
    extra_context={'name': 'value'},      # 額外上下文
    output_dir='.',                        # 輸出目錄
    overwrite_if_exists=False,            # 是否覆蓋
)

# 從本地範本
cookiecutter('path/to/template', no_input=True)
```

### 核心函數
- `cookiecutter(template, ...)` - 主函數
- `generate_context(template_dir, ...)` - 生成上下文
- `generate_files(repo_dir, ...)` - 生成檔案
- `prompt_for_config(template_dir, ...)` - 互動提示

---

## 4. pydantic_core - Pydantic 核心驗證

### 模組結構
- `pydantic_core/__init__.py` - 主要導出
- `pydantic_core/core_schema.py` - Schema 定義

### 主要 API (核心為 Cython 編譯)

```python
from pydantic_core import (
    SchemaValidator,
    SchemaSerializer,
    ValidationError,
    Some,
    Url,
    MultiHostUrl,
    to_json,
    from_json,
    __version__,
)

# 建立驗證器
validator = SchemaValidator({
    "type": "model",
    "class_name": "MyModel",
    "fields": {
        "name": {"type": "str"},
        "age": {"type": "int"}
    }
})

# 驗證資料
try:
    result = validator.validate_python({"name": "John", "age": 30})
except ValidationError as e:
    print(e.errors())

# 序列化
json_data = validator.to_json(result)
```

### 關鍵類別
- `SchemaValidator` - Schema 驗證器
- `SchemaSerializer` - Schema 序列化器
- `ValidationError` - 驗證錯誤
- `Url` / `MultiHostUrl` - URL 類型

---

## 5. anyio - 異步 IO 庫

### 模組結構
- `anyio/_core/` - 核心功能 (eventloop, tasks, synchronization)
- `anyio/_backends/` - 後端實現
- `anyio/streams/` - 數據流
- `anyio/to_thread.py` - 執行緒池

### 主要 API

```python
import anyio

# 執行異步函數
anyio.run(async_function)

# 基本異步操作
async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(some_async_function)
    
    # 同步原語
    async with anyio.Lock() as lock:
        async with lock:
            pass
    
    # 容量限制
    limiter = anyio.CapacityLimiter(5)
    async with limiter:
        pass
    
    # 超時控制
    with anyio.fail_after(5):
        await some_async_function()
    
    # 建立 TCP 連接
    stream = await anyio.connect_tcp('example.com', 80)
    
    # 内置取消作用域
    with anyio.move_on_after(1):
        await asyncio.sleep(10)

# 文件操作
async with anyio.open_file('test.txt', 'r') as f:
    content = await f.read()

# 子進程
async with anyio.open_process(['ls']) as proc:
    async for line in proc.stdout:
        print(line)
```

### 關鍵類別/函數
- `run()` - 執行 async 函數
- `Lock`, `Event`, `Semaphore`, `Condition` - 同步原語
- `CapacityLimiter` - 容量限制
- `CancelScope` - 取消作用域
- `create_task_group()` - 任務組
- `connect_tcp()`, `create_tcp_listener()` - TCP 網路

---

## 6. httptools - HTTP 協議解析

### 模組結構
- `httptools/parser/` - 解析器實現
- `httptools/parser/protocol.py` - HTTPProtocol
- `httptools/parser/url_parser.py` - URL 解析

### 主要 API

```python
from httptools import (
    HttpRequestParser,
    HttpResponseParser,
    parse_url,
    ParserError,
)

# HTTP 請求解析
class MyRequestHandler:
    def __init__(self):
        self.parser = HttpRequestParser(self)
    
    def on_message_begin(self):
        pass
    
    def on_message_complete(self):
        pass
    
    def on_header(self, name, value):
        pass
    
    def on_body(self, body):
        pass
    
    def on_headers_complete(self, headers):
        pass
    
    def on_message_complete(self):
        pass

# URL 解析
from httptools import parse_url
url = parse_url('http://example.com:8080/path?query=value')
print(url.host)  # example.com
print(url.port)  # 8080
print(url.path)  # /path
```

### 關鍵類別
- `HttpRequestParser` - HTTP 請求解析器
- `HttpResponseParser` - HTTP 回應解析器
- `parse_url()` - URL 解析函數
- `ParserError` - 解析錯誤

---

## 7. httpcore - HTTP 客戶端核心

### 模組結構
- `httpcore/_sync/` - 同步實現
- `httpcore/_async/` - 異步實現
- `httpcore/_models.py` - 數據模型
- `httpcore/_exceptions.py` - 例外

### 主要 API

```python
import httpcore

# 簡單請求
response = httpcore.request('GET', 'https://example.com')
print(response.status_code)
print(response.content)

# 連接池
with httpcore.ConnectionPool() as pool:
    response = pool.request('GET', 'https://example.com')

# 同步/異步連接
from httpcore import HTTPConnection, HTTP11Connection, HTTP2Connection
from httpcore import AsyncHTTPConnection, AsyncConnectionPool

# 代理支援
from httpcore import HTTPProxy
proxy = HTTPProxy(forward_lazy='http://proxy:8080')

# 數據模型
from httpcore import Request, Response, URL, Origin
request = Request(
    method='POST',
    url='https://api.example.com/data',
    content=b'{"key": "value"}',
    headers={'Content-Type': 'application/json'}
)
```

### 關鍵類別
- `Request` / `Response` - 請求/回應模型
- `HTTPConnection` - HTTP/1.1 連接
- `HTTP2Connection` - HTTP/2 連接
- `ConnectionPool` - 連接池
- `HTTPProxy` - HTTP 代理

---

## 8. tenacity - 重試機制庫

### 模組結構
- `tenacity/__init__.py` - 主模組
- `tenacity/retry.py` - 重試策略
- `tenacity/stop.py` - 停止策略
- `tenacity/wait.py` - 等待策略
- `tenacity/`asyncio/` - 異步支援

### 主要 API

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),              # 最多重試 3 次
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 指數退避
    retry=retry_if_exception_type(IOError),  # 只重試 IOError
    before_sleep=lambda retry_state: print(f"Retrying..."),
)
def my_function():
    # 可能失敗的操作
    pass

# 手動使用
from tenacity import Retrying
for attempt in Retrying(
    stop=stop_after_attempt(5),
    wait=wait_exponential(),
):
    with attempt:
        my_function()
```

### 預設重試策略
- `retry_if_exception_type(exc_type)` - 指定異常類型
- `retry_if_result(predicate)` - 根據結果判斷
- `retry_always` / `retry_never` - 總是重試/永不重試

### 預設停止策略
- `stop_after_attempt(n)` - 嘗試次數
- `stop_after_delay(seconds)` - 總延遲時間

### 預設等待策略
- `wait_fixed(seconds)` - 固定等待
- `wait_exponential()` - 指數退避
- `wait_random()` - 隨機等待

---

## 9. sniffio - 異步庫檢測

### 模組結構
- `sniffio/_impl.py` - 實現

### 主要 API

```python
import sniffio

# 檢測當前異步庫
library = sniffio.current_async_library()

# 拋出異常而非返回 None
library = sniffio.current_async_library(require=True)

# 執行緒本地存儲
sniffio.thread_local

# 自定義異步庫
sniffio.current_async_library_cvar.set("asyncio")
```

### 關鍵函數
- `current_async_library()` - 取得當前異步庫名稱 ('asyncio', 'trio', 'curio')
- `AsyncLibraryNotFoundError` - 未檢測到異步庫時拋出

---

## 10. 網路底層庫

### certifi - CA 憑證

```python
import certifi

cert_path = certifi.where()  # 返回 CA bundle 路徑
cert_content = certifi.contents()  # 返回 CA bundle 內容
```

### idna - 國際化域名

```python
import idna

# 編碼/解碼國際化域名
encoded = idna.encode('münchen.de')  # b'xn--mnchen-3ya.de'
decoded = idna.decode('xn--mnchen-3ya.de')  # 'münchen.de'

# 驗證
idna.check_label('example')  # 驗證標籤
idna.valid_label_length(label)  # 檢查長度

# 異常類別
# IDNAError, IDNABidiError, InvalidCodepoint, InvalidCodepointContext
```

### urllib3 - HTTP 客戶端

```python
import urllib3

# 簡單請求
response = urllib3.request('GET', 'https://example.com')

# 連接池
with urllib3.HTTPConnectionPool('example.com') as pool:
    response = pool.request('GET', '/path')

# 數據模型
from urllib3 import HTTPHeaderDict, Retry, Timeout, PoolManager
from urllib3.response import HTTPResponse

# 重試配置
retry = Retry(total=3, backoff_factor=0.1)
timeout = Timeout(connect=5.0, read=10.0)

# PoolManager 用於管理多個連接池
manager = urllib3.PoolManager()
```

### charset_normalizer - 字元編碼檢測

```python
from charset_normalizer import from_bytes, from_path, from_fp, detect

# 從位元組檢測編碼
results = from_bytes(b'\xc3\xa9\xc3\xa0 \xc3\xb1')
best = results.best()
print(best)  # 'utf-8'

# 從檔案檢測
matches = from_path('document.txt')

# 從檔案指標檢測
with open('file.txt', 'rb') as fp:
    matches = from_fp(fp)

# 舊 API (chardet 相容)
result = detect(b'\xc3\xa9...\xfa')
encoding = result['encoding']
confidence = result['confidence']

# 主要類別
from charset_normalizer import CharsetMatch, CharsetMatches
```

---

## 11. 其他常用資訊

### 異步庫對照

| 功能 | asyncio | anyio | trio |
|------|---------|-------|------|
| 執行 | `asyncio.run()` | `anyio.run()` | `trio.run()` |
| 任務 | `asyncio.create_task()` | `task_group.start_soon()` | `nursery.start_soon()` |
| 鎖 | `asyncio.Lock()` | `anyio.Lock()` | `trio.Lock()` |
| 超時 | `asyncio.wait_for()` | `anyio.fail_after()` | `trio.move_on_after()` |

### 常用重試模式

```python
# 指數退避 + 重試次數限制
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60)
)
def api_call_with_retry():
    pass

# HTTP 客戶端重試
import urllib3
from urllib3.util.retry import Retry
from urllib3.request import Request

retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
```

---

## 12. 在專案中的可能應用場景

1. **rich** - 翻譯工具的 CLI 輸出美化
2. **click** - 構建翻譯工具的命令列介面
3. **anyio** - 異步網路請求優化
4. **httpcore/urllib3** - HTTP 客戶端基礎
5. **tenacity** - API 請求重試機制
6. **charset_normalizer** - 檢測翻譯來源文件的編碼

---

*筆記完成*
