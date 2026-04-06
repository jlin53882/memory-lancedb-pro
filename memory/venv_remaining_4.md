# Minecraft_translator_flet venv 套件筆記 (4/4)

> 涵蓋範圍：text_unidecode, typing_inspection, tzdata, watchfiles, wheel, wikipedia, yaml, _yaml

---

## 1. text_unidecode

**用途**：將 Unicode 字元轉換為 ASCII 字元（用於翻譯/音譯）。

### 模組結構
```
text_unidecode/
├── __init__.py
└── data.bin (編碼查詢表)
```

### 主要函數

```python
def unidecode(txt: str) -> str:
    """將 Unicode 字元轉換為 ASCII"""
```

**使用範例**：
```python
from text_unidecode import unidecode
unidecode("你好")  # -> "Ni Hao"
unidecode("Minecraft")  # -> "Minecraft"
```

### 筆記
- 內建一個大型查詢表 (data.bin)，包含 Unicode codepoint 到 ASCII 的映射
- 針對中文、日文、韓文等非 ASCII 字元做音譯
- 簡單直接，無配置選項

---

## 2. typing_inspection

**用途**：提供 Python 類型註釋的高階與低階內省工具。

### 模組結構
```
typing_inspection/
├── __init__.py
├── introspection.py      # 高階 API
├── typing_objects.py      # 低階 API
├── typing_objects.pyi    # 類型存根
└── py.typed
```

### 主要 API

#### 低階 API (typing_objects.py)
```python
# 類型判斷函數 - 簽名皆為 (obj: Any) -> bool
is_annotated(obj)        # 是否為 Annotated
is_any(obj)              # 是否為 Any
is_classvar(obj)         # 是否為 ClassVar
is_final(obj)            # 是否為 Final
is_generic(obj)          # 是否為 Generic
is_literal(obj)          # 是否為 Literal
is_namedtuple(obj)       # 是否為 NamedTuple
is_never(obj)            # 是否為 Never
is_newtype(obj)          # 是否為 NewType
is_nodefault(obj)        # 是否為 NoDefault
is_noreturn(obj)         # 是否為 NoReturn
is_notrequired(obj)      # 是否為 NotRequired
is_paramspec(obj)        # 是否為 ParamSpec
is_readonly(obj)         # 是否為 ReadOnly
is_required(obj)         # 是否為 Required
is_typevar(obj)          # 是否為 TypeVar
is_typevartuple(obj)     # 是否為 TypeVarTuple
is_union(obj)            # 是否為 Union
is_typealiastype(obj)    # 是否為 TypeAliasType
```

#### 高階 API (introspection.py)
```python
# 檢視註釋表達式
def inspect_annotation(
    annotation: Any,
    *,
    annotation_source: AnnotationSource,
    unpack_type_aliases: Literal['skip', 'lenient', 'eager'] = 'skip'
) -> InspectedAnnotation:
    """
    提取類型註釋中的 qualifiers 和 metadata
    """

# 取得 Literal 的值
def get_literal_values(
    annotation: Any,
    *,
    type_check: bool = False,
    unpack_type_aliases: Literal['skip', 'lenient', 'eager'] = 'eager'
) -> Generator[Any]:
    """Yield Literal[...] 中的所有值"""

# 類別
class AnnotationSource(IntEnum):
    """註釋來源類型"""
    ASSIGNMENT_OR_VARIABLE = auto()
    CLASS = auto()
    DATACLASS = auto()
    TYPED_DICT = auto()
    NAMED_TUPLE = auto()
    FUNCTION = auto()
    ANY = auto()
    BARE = auto()

class InspectedAnnotation(NamedTuple):
    type: Any | _UnkownType      # 類型表達式
    qualifiers: set[Qualifier]   # 類型限定符
    metadata: list[Any]          # Annotated metadata
```

**使用範例**：
```python
from typing_inspection import typing_objects, inspect_annotation, AnnotationSource

# 檢查類型
typing_objects.is_final(Final)    # -> True
typing_objects.is_final(Final[int])  # -> False

# 檢視註釋
result = inspect_annotation(
    Final[Annotated[int, 'meta']],
    annotation_source=AnnotationSource.CLASS
)
# InspectedAnnotation(type=int, qualifiers={'final'}, metadata=['meta'])
```

### 筆記
- 支援 Python 3.10+
- 處理 PEP 695 類型別名
-typing_objects 是低階實現，用於判斷各類型的「身份」
- introspection 是高階封裝，用於解析複雜的註釋結構

---

## 3. tzdata

**用途**：提供 IANA 時區資料庫的純 Python 實現。

### 模組結構
```
tzdata/
├── __init__.py (版本資訊)
├── zones (時區別名映射)
└── zoneinfo/  (時區資料目錄)
    ├── Africa/
    ├── America/
    ├── Asia/
    ├── Europe/
    ├── Pacific/
    ├── US/
    └── [其他區域]
```

### 主要內容
```python
__version__ = "2025.2"
IANA_VERSION = "2025b"
```

### 筆記
- tzdata 本身不提供直接 API，是一個資料包
- 配合 Python 內建的 `zoneinfo` 模組使用
- 當系統沒有 IANA 時區資料時，可透過此套件提供
- 資料檔案為二進制 TZif 格式

---

## 4. watchfiles

**用途**：監控檔案系統變更，適用於開發時自動重啟服務。

### 模組結構
```
watchfiles/
├── __init__.py
├── main.py         # watch/awatch
├── run.py          # run_process/arun_process
├── filters.py      # 過濾器
├── cli.py          # 命令列工具
├── version.py
├── _rust_notify.cp312-win_amd64.pyd  # Rust 擴展
└── _rust_notify.pyi
```

### 主要 API

```python
class Change(IntEnum):
    added = 1      # 檔案/目錄新增
    modified = 2  # 檔案/目錄修改
    deleted = 3   # 檔案/目錄刪除

# 同步監控
def watch(
    *paths: Union[Path, str],
    watch_filter: Optional[Callable[[Change, str], bool]] = DefaultFilter(),
    debounce: int = 1_600,           # 毫秒，合併變更的等待時間
    step: int = 50,                   # 毫秒，檢查間隔
    stop_event: Optional['AbstractEvent'] = None,
    rust_timeout: int = 5_000,
    yield_on_timeout: bool = False,
    debug: Optional[bool] = None,
    raise_interrupt: bool = True,
    force_polling: Optional[bool] = None,
    poll_delay_ms: int = 300,
    recursive: bool = True,
    ignore_permission_denied: Optional[bool] = None,
) -> Generator[Set[FileChange], None, None]:
    """
    監控檔案變更並 yield 變更集合
    """

# 異步監控
async def awatch(
    *paths: Union[Path, str],
    # ... 參數類似 watch
) -> AsyncGenerator[Set[FileChange], None]:
    """異步版本的 watch"""

# 執行並監控重啟
def run_process(
    *paths: Union[Path, str],
    target: Union[str, Callable[..., Any]],
    args: Tuple[Any, ...] = (),
    kwargs: Optional[Dict[str, Any]] = None,
    target_type: Literal['function', 'command', 'auto'] = 'auto',
    callback: Optional[Callable[[Set[FileChange]], None]] = None,
    grace_period: float = 0,
    # ... 其他參數
) -> int:
    """執行程序並在檔案變更時自動重啟"""

# 異步版本
async def arun_process(...):
    """異步版本的 run_process"""
```

**使用範例**：
```python
from watchfiles import watch, Change

# 基本用法
for changes in watch('./src'):
    print(f"Files changed: {changes}")

# 過濾特定副檔名
from watchfiles import DefaultFilter
for changes in watch('./src', watch_filter=DefaultFilter(patterns=['*.py'])):
    print(f"Python files changed: {changes}")

# 執行並重啟
from watchfiles import run_process
run_process('.', target='python', args=('main.py',))
```

### 筆記
- 底層使用 Rust 實現 (notify crate) + Python 封裝
- 支援 force_polling 模式（環境變數 `WATCHFILES_FORCE_POLLING`）
- 預設過濾 `.pyc`、`__pycache__`、隱藏檔案
- 常見於 uvicorn、hypercorn 等 ASGI 伺服器的開發模式

---

## 5. wheel

**用途**：建置 Python wheel 套件的工具。

### 模組結構
```
wheel/
├── __init__.py (版本資訊)
├── bdist_wheel.py
├── _bdist_wheel.py
├── metadata.py
├── wheelfile.py
├── util.py
├── cli/          # 命令列工具
│   ├── convert.py
│   ├── pack.py
│   ├── tags.py
│   └── unpack.py
└── vendored/     # 依賴的 packaging 庫
    └── packaging/
        ├── specifiers.py
        ├── tags.py
        └── version.py
```

### 主要內容
```python
__version__ = "0.45.1"
```

### 筆記
- wheel 是 setuptools 的幕後元件
- 主要用於將套件打包成 .whl 格式
- CLI 工具可獨立使用：`python -m wheel`
-  vendored 包裝了 `packaging` 庫（版本比對、標籤等）

---

## 6. wikipedia

**用途**：Wikipedia API 的 Python 封裝。

### 模組結構
```
wikipedia/
├── __init__.py
├── wikipedia.py    # 主要 API
├── exceptions.py   # 例外定義
└── util.py        # 工具函數
```

### 主要 API

```python
# 全域設定
def set_lang(prefix: str) -> None:
    """設定語言前綴，如 'zh', 'en', 'ja'"""

def set_user_agent(user_agent_string: str) -> None:
    """設定 User-Agent"""

def set_rate_limiting(rate_limit: bool, min_wait: timedelta = ...) -> None:
    """啟用/停用速率限制"""

# 搜尋與摘要
@cache
def search(query: str, results: int = 10, suggestion: bool = False):
    """Wikipedia 搜尋"""

@cache
def suggest(query: str) -> str | None:
    """取得搜尋建議"""

@cache
def summary(
    title: str,
    sentences: int = 0,
    chars: int = 0,
    auto_suggest: bool = True,
    redirect: bool = True
) -> str:
    """取得頁面摘要"""

@cache
def geosearch(latitude, longitude, title=None, results=10, radius=1000):
    """地理搜尋"""

def random(pages: int = 1) -> str | list[str]:
    """隨機頁面"""

# 頁面物件
def page(
    title: str = None,
    pageid: int = None,
    auto_suggest: bool = True,
    redirect: bool = True,
    preload: bool = False
) -> WikipediaPage:
    """取得 WikipediaPage 物件"""

class WikipediaPage:
    """Wikipedia 頁面封裝"""
    
    @property
    def content(self) -> str:      # 頁面正文
    @property
    def summary(self) -> str:      # 摘要
    @property
    def images(self) -> list[str]: # 圖片 URLs
    @property
    def links(self) -> list[str]:   # 連結標題
    @property
    def categories(self) -> list[str]:  # 分類
    @property
    def sections(self) -> list[str]:    # 章節標題
    @property
    def references(self) -> list[str]:  # 引用
    @property
    def coordinates(self) -> tuple:     # 座標
    
    def section(self, section_title: str) -> str | None:
        """取得特定章節內容"""
    
    def html(self) -> str:
        """取得原始 HTML"""
```

**使用範例**：
```python
import wikipedia

# 設定語言
wikipedia.set_lang('zh')

# 搜尋
results = wikipedia.search('Python')
print(results)  # ['Python', 'Python (程式語言)', ...]

# 取得摘要
summary = wikipedia.summary('Python')
print(summary)

# 取得頁面
page = wikipedia.page('Python (程式語言)')
print(page.content)       # 正文
print(page.images)        # 圖片
print(page.sections)      # 章節

# 取得章節內容
intro = page.section('歷史')
```

### 例外
```python
from wikipedia.exceptions import (
    PageError,       # 頁面不存在
    DisambiguationError,  # 消歧義頁面
    RedirectError,   # 重新導向錯誤
    HTTPTimeoutError # HTTP 超時
)
```

### 筆記
- 預設語言是英文
- 搜尋結果會自動快取
- 需注意速率限制，避免被 Wikipedia API 封鎖

---

## 7. yaml (PyYAML)

**用途**：YAML 解析與序列化。

### 模組結構
```
yaml/
├── __init__.py       # 主 API
├── dumper.py         # Dumper 類
├── loader.py        # Loader 類
├── cyaml.py         # C 擴展封裝
├── emitter.py       # YAML 輸出
├── parser.py        # YAML 解析
├── scanner.py       # 詞法掃描
├── constructor.py   # 節點建構
├── resolver.py      # 類型解析
├── representer.py   # 物件表示
├── composer.py      # 節點組合
├── reader.py        # 輸入處理
├── serializer.py    # 序列化
├── error.py         # 例外
├── events.py       # 事件
├── nodes.py        # 節點
├── tokens.py       # Token
└── _yaml.cp312-win_amd64.pyd  # C 擴展
```

### 主要 API

```python
__version__ = '6.0.3'
__with_libyaml__ = True  # C 擴展可用

# ============ 載入 ============

def safe_load(stream):
    """安全載入（僅解析基本類型）"""

def safe_load_all(stream):
    """安全載入多個文件"""

def full_load(stream):
    """完整載入（解析所有標籤，可能不安全）"""

def full_load_all(stream):
    """完整載入多個文件"""

def unsafe_load(stream):
    """不安全載入（解析所有標籤）"""

def load(stream, Loader):
    """自訂 Loader 載入"""

def load_all(stream, Loader):
    """自訂 Loader 載入多個文件"""

# ============ 傾出 ============

def safe_dump(data, stream=None):
    """安全傾出"""

def safe_dump_all(documents, stream=None):
    """安全傾出多個文件"""

def dump(data, stream=None, Dumper=Dumper, **kwds):
    """自訂 Dumper 傾出"""

def dump_all(documents, stream=None, Dumper=Dumper, **kwds):
    """自訂 Dumper 傾出多個文件"""

# ============ 低階 API ============

def scan(stream, Loader=Loader):
    """掃描產生 tokens"""

def parse(stream, Loader=Loader):
    """解析產生 events"""

def compose(stream, Loader=Loader):
    """解析產生單一節點樹"""

def compose_all(stream, Loader=Loader):
    """解析產生所有節點樹"""

def emit(events, stream=None, Dumper=Dumper, ...):
    """發射事件到串流"""
```

### Loader/Dumper 類別

```python
# Loader
class Loader:      # 基本載入器
class SafeLoader:  # 安全載入器
class FullLoader:  # 完整載入器（默認）
class UnsafeLoader: # 不安全載入器

# Dumper
class Dumper:      # 基本傾出器
class SafeDumper:  # 安全傾出器
```

**使用範例**：
```python
import yaml

# 載入
with open('config.yaml') as f:
    data = yaml.safe_load(f)

# 傾出
with open('output.yaml', 'w') as f:
    yaml.dump(data, f, allow_unicode=True)

# 使用 C 擴展（更快）
from yaml import CLoader as Loader, CDumper as Dumper
data = yaml.load(f, Loader=Loader)
```

### 筆記
- C 擴展 (_yaml) 可大幅提升效能
- `safe_load` 是最安全的選擇，推薦用於不受信任的輸入
- 支援自訂類型的建構函數和表示函數

---

## 8. _yaml (PyYAML C 擴展)

**用途**：PyYAML 的 C 語言擴展，提供更快解析速度。

### 模組結構
```
_yaml/
├── __init__.py  # Stub 包
└── _yaml.cp312-win_amd64.pyd  # 編譯的 C 擴展
```

### 主要內容

_yaml 現已整合到 yaml 包中，作為 yaml._yaml 存在。

```python
# _yaml/__init__.py 的行為：
# 1. 嘗試 import yaml 並檢查 __with_libyaml__
# 2. 如果沒有 LibYAML，拋出 ModuleNotFoundError
# 3. 如果有，從 yaml._yaml 匯出內容
# 4. 發出 DeprecationWarning，建議直接從 yaml 匯入
```

### 筆記
- 這是一個橋接套件，歷史原因存在
- 推薦用法：
  ```python
  # 新代碼應使用：
  from yaml import CLoader, CDumper
  
  # 而非：
  from _yaml import CLoader  # 已廢棄
  ```
- 在 Windows 上為 .pyd 檔案（等同 Linux 的 .so）

---

## 總結

| 套件 | 版本 | 用途 |
|------|------|------|
| text_unidecode | 1.3 | Unicode → ASCII 音譯 |
| typing_inspection | 0.4.2 | 類型註釋內省 |
| tzdata | 2025.2 | IANA 時區資料 |
| watchfiles | 1.1.1 | 檔案監控/熱重載 |
| wheel | 0.45.1 | Wheel 打包工具 |
| wikipedia | 1.4.0 | Wikipedia API |
| yaml | 6.0.3 | YAML 解析 |
| _yaml | - | PyYAML C 擴展 |
