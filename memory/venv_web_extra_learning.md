# Venv 套件學習筆記 (Web 相關)

> 來源：`C:\Users\admin\Desktop\minecraft_translator_flet\.venv\Lib\site-packages`
> 日期：2026-03-15

---

## 1. BeautifulSoup4 (bs4) - HTML/XML 解析

### 模組結構
```
bs4/
├── __init__.py       # 主要導出：BeautifulSoup, Tag, NavigableString
├── element.py        # PageElement, Tag, NavigableString 定義
├── builder/         # 解析器 builder
├── filter.py        # SoupStrainer, ElementFilter
├── formatter.py     # HTMLFormatter, XMLFormatter
└── exceptions.py    # 例外類別
```

### 主要類別與簽名

#### BeautifulSoup
```python
class BeautifulSoup(Tag):
    def __init__(
        self,
        markup: _IncomingMarkup = "",
        features: Optional[Union[str, Sequence[str]]] = None,
        builder: Optional[Union[TreeBuilder, Type[TreeBuilder]]] = None,
        parse_only: Optional[SoupStrainer] = None,
        from_encoding: Optional[_Encoding] = None,
        exclude_encodings: Optional[_Encodings] = None,
        element_classes: Optional[Dict[Type[PageElement], Type[PageElement]]] = None,
        **kwargs: Any,
    )
```
- **功能**：解析 HTML/XML 文檔的主要入口
- **features**：指定解析器 ("lxml", "html.parser", "html5lib")

#### Tag
```python
class Tag(PageElement):
    def __init__(
        self,
        parser: Optional[BeautifulSoup] = None,
        builder: Optional[TreeBuilder] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        prefix: Optional[str] = None,
        attrs: Optional[_RawOrProcessedAttributeValues] = None,
        parent: Optional[Union[BeautifulSoup, Tag]] = None,
        previous: _AtMostOneElement = None,
        is_xml: Optional[bool] = None,
        # ... 更多參數
    )
```

#### NavigableString
```python
class NavigableString(str, PageElement):
    # 用於表示標籤內的文本內容
```

### 重要 API 用法

```python
from bs4 import BeautifulSoup

# 解析 HTML
soup = BeautifulSoup(html_string, 'lxml')

# 查找元素
soup.find('div')                    # 找第一個
soup.find_all('a', class_='link')   # 找全部
soup.select('.css-selector')         # CSS 選擇器

# 獲取內容
soup.title.string                    # 標籤內容
soup.find('a')['href']               # 屬性值
soup.get_text(separator='|')         # 獲取所有文本

# 修改文檔
new_tag = soup.new_tag('a', href='http://example.com')
soup.body.append(new_tag)

# 輸出
soup.prettify()                     # 格式化輸出
soup.decode()                       # 轉為字串
```

---

## 2. Starlette - ASGI 框架

### 模組結構
```
starlette/
├── __init__.py           # 版本資訊
├── routing.py            # 路由系統
├── requests.py           # Request 類別
├── responses.py          # Response 類別
├── applications.py       # Starlette 應用
├── middleware/           # 中間件
├── authentication.py     # 認證
├── exceptions.py         # HTTP 例外
├── websockets.py         # WebSocket 支援
├── testclient.py         # 測試客戶端
└── staticfiles.py       # 靜態檔案
```

### 主要類別與簽名

#### Application
```python
class Starlette(ASGIApp):
    def __init__(
        self: ASGIApp,
        debug: bool = False,
        routes: Sequence[BaseRoute] | None = None,
        middleware: Sequence[Middleware] | None = None,
        exception_handlers: dict[int | type[Exception], callable] | None = None,
        lifespan: Lifespan[dict[Any, Any]] | None = None,
        # ...
    )
```

#### Route
```python
class Route(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Collection[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: Sequence[Middleware] | None = None,
    ) -> None
```

#### Request
```python
class Request(scope: Scope, receive: Receive = ..., send: Send = ...):
    @property
    def method(self) -> str
    @property
    def url(self) -> URL
    @property
    def headers(self) -> Headers
    @property
    def query_params(self) -> QueryParams
    @property
    def path_params(self) -> dict[str, Any]
    async def json(self) -> Any
    async def form(self) -> FormData
```

#### Response
```python
class Response(
    content: bytes | str = b"",
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    media_type: str | None = None,
    background: BackgroundTask | None = None,
) -> None

# 常見 Response 子類別
class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200, ...)
class HTMLResponse(Response):
class PlainTextResponse(Response):
class RedirectResponse(Response):
class FileResponse(Response):
```

### 重要 API 用法

```python
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, HTMLResponse
from starlette.requests import Request

# 建立應用
app = Starlette(
    debug=True,
    routes=[
        Route('/hello', endpoint=hello),
        Route('/users/{user_id:int}', endpoint=get_user),
        Mount('/static', app=StaticFiles(directory='static')),
    ]
)

# 端點函式
async def hello(request: Request):
    return JSONResponse({'message': 'Hello'})

async def get_user(request: Request):
    user_id = request.path_params['user_id']
    return JSONResponse({'id': user_id})

# 使用 Path 轉換器
from starlette.convertors import IntConvertor, StringConvertor
# 內建：int, str, float, path, uuid
```

---

## 3. markdown_it - Markdown 解析

### 模組結構
```
markdown_it/
├── __init__.py           # MarkdownIt 導出
├── main.py               # 主要類別
├── parser_block.py       # 區塊解析
├── parser_inline.py      # 行內解析
├── parser_core.py        # 核心解析
├── renderer.py           # 渲染器
├── token.py              # Token 類別
├── ruler.py              # 規則管理
├── presets/             # 預設配置
│   ├── commonmark.py
│   ├── default.py
│   └── ...
└── common/               # 工具函數
```

### 主要類別與簽名

#### MarkdownIt
```python
class MarkdownIt:
    def __init__(
        self,
        config: str | PresetType = "commonmark",
        options_update: Mapping[str, Any] | None = None,
        *,
        renderer_cls: Callable[[MarkdownIt], RendererProtocol] = RendererHTML,
    )
```

### 重要 API 用法

```python
from markdown_it import MarkdownIt

# 建立解析器
md = MarkdownIt('commonmark')  # 支援: commonmark, default, gfm-like, zero
md = MarkdownIt().enable('smartquotes').disable('link')

# 解析與渲染
tokens = md.parse(markdown_string)     # 解析為 token 流
html = md.render(markdown_string)      # 直接輸出 HTML
html_inline = md.renderInline(md_str)  # 行內渲染（無 <p> 標籤）

# 解析為 token（用於自定義渲染）
tokens = md.parse(src, env=None)

# 添加規則
def my_plugin(md):
    def render_foo(tokens, idx, options, env, renderer):
        return f'<custom>{tokens[idx].content}</custom>'
    md.add_render_rule('foo', render_foo)

md.use(my_plugin)

# 預設 preset
md = MarkdownIt("commonmark")    # CommonMark 標準
md = MarkdownIt("default")       # 預設（包含表格、代碼圍欄等）
md = MarkdownIt("gfm-like")     # GitHub 風格
```

---

## 4. Jinja2 - 模板引擎

### 模組結構
```
jinja2/
├── __init__.py           # 導出：Environment, Template, Loader
├── environment.py        # Environment 類別
├── template.py           # Template 類別
├── lexer.py              # 詞法分析
├── parser.py             # 語法分析
├── compiler.py           # 代碼生成
├── runtime.py            # 執行期上下文
├── filters.py            # 內建過濾器
├── tests.py              # 內建測試
├── loaders.py            # 模板載入器
├── ext.py                # 擴展
├── sandbox.py            # 沙盒環境
└── exceptions.py         # 例外
```

### 主要類別與簽名

#### Environment
```python
class Environment:
    def __init__(
        self,
        block_start_string: str = "{%",
        block_end_string: str = "%}",
        variable_start_string: str = "{{",
        variable_end_string: str = "}}",
        comment_start_string: str = "{#",
        comment_end_string: str = "#}",
        line_statement_prefix: str | None = None,
        trim_blocks: bool = False,
        lstrip_blocks: bool = False,
        loader: BaseLoader | None = None,
        autoescape: bool | Callable[[str], bool] = False,
        enable_async: bool = False,
        # ... 更多參數
    )
```

#### Template
```python
class Template:
    def __init__(self, source: str, blocks: dict | None = None, env: Environment | None = None)
    
    # 渲染方法
    def render(self, **context: Any) -> str
    async def render_async(self, **context: Any) -> str
    def stream(self, **context: Any) -> TemplateStream
    def generate(self, **context: Any) -> Iterator[str]
```

### 重要 API 用法

```python
from jinja2 import Environment, FileSystemLoader, Template

# 基本用法
env = Environment(loader=FileSystemLoader('templates/'))
template = env.get_template('page.html')
html = template.render(title='Hello', items=['a', 'b', 'c'])

# 直接使用字串
template = Template('Hello {{ name }}!')
template.render(name='World')

# 內建過濾器
{{ name|upper }}
{{ items|join(', ') }}
{{ content|striptags }}
{{ number|round(1) }}

# 控制結構
{% for item in items %}
  {{ item }}
{% endfor %}

{% if user %}
  Hello {{ user.name }}
{% endif %}

# 巨集
{% macro input(name, value='', type='text') %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{{ input('username') }}

# 擴展
env = Environment(extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.i18n'])

# 非同步
env = Environment(enable_async=True)
async_template = env.from_string("Hello {{ name }}")
html = await async_template.render_async(name="World")

# 自定義過濾器
env.filters['markdown'] = markdown_filter

# 載入器
loader = FileSystemLoader('templates/')
loader = PackageLoader('mypackage', 'templates')
loader = DictLoader({'page.html': '<h1>{{ page }}</h1>'})
```

---

## 5. PyYAML - YAML 解析/序列化

### 模組結構
```
yaml/
├── __init__.py           # 導出主要函數
├── loader.py             # Loader 類別
├── dumper.py             # Dumper 類別
├── constructor.py        # 物件建構
├── representer.py        # 物件表示
├── parser.py            # 解析器
├── scanner.py            # 掃描器
├── emitter.py            # 發射器
├── nodes.py              # 節點類別
├── events.py             # 事件類別
└── error.py              # 例外
```

### 主要類別與簽名

#### Loader (已棄用，請用 SafeLoader/FullLoader)
```python
# 請使用以下載入器：
SafeLoader    # 安全：只解析基本類型
FullLoader    # 安全：完整解析（預設）
UnsafeLoader  # 不安全：可執行任意 Python 物件

# Dumper
SafeDumper    # 安全序列化
Dumper        # 完整序列化
```

### 重要 API 用法

```python
import yaml

# 載入 YAML
data = yaml.safe_load('name: John\nage: 30')  # 單文檔
data_list = yaml.safe_load_all('doc1\n---\ndoc2\n')  # 多文檔

# 讀取檔案
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# 序列化 YAML
yaml.dump({'name': 'John', 'age': 30})  # 輸出字串
yaml.dump(data, file, default_flow_style=False)  # 區塊樣式

# 安全載入（推薦用於不受信任的輸入）
yaml.safe_load(untrusted_yaml)

# 自定義類型
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# 添加建構器
def person_constructor(loader, node):
    return Person(**loader.construct_mapping(node))

yaml.add_constructor('!person', person_constructor, Loader=yaml.SafeLoader)

# 添加表示器
def person_representer(dumper, person):
    return dumper.represent_mapping('!person', {'name': person.name, 'age': person.age})

yaml.add_representer(Person, person_representer)

# YAML 與 Python 物件
yaml.dump(obj, default_flow_style=False)  # 區塊樣式（人類可讀）
yaml.dump(obj, default_flow_style=True)    # 流樣式（緊湊）
```

---

## 6. 快速參考表

| 套件 | 主要類別 | 常用方法 |
|------|---------|---------|
| **bs4** | BeautifulSoup | `find()`, `find_all()`, `select()`, `get_text()` |
| **starlette** | Starlette, Route, Request, Response | `app.run()`, `request.json()`, `JSONResponse()` |
| **markdown_it** | MarkdownIt | `render()`, `parse()`, `enable()`, `disable()` |
| **jinja2** | Environment, Template | `get_template()`, `render()`, `stream()` |
| **pyyaml** | SafeLoader, SafeDumper | `safe_load()`, `dump()`, `safe_dump()` |

---

## 7. 版本資訊

- beautifulsoup4: 4.14.2
- starlette: 0.48.0
- markdown_it: 4.0.0
- jinja2: 3.1.6
- pyyaml: 6.0.3
