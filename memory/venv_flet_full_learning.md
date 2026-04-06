# Flet venv 套件原始碼完整學習筆記

> 版本：flet 0.28.3 | 建立日期：2026-03-15

---

## 1. flet（核心 UI 框架）

### 1.1 模組結構

```
flet/
├── __init__.py          # 主入口，導出所有 UI 元件
├── app.py               # app() / app_async() 應用程式啟動函數
├── cli.py               # CLI 入口
├── core/                # 核心 UI 元件（最多）
│   ├── page.py          # Page 類別
│   ├── control.py       # Control 基底類別
│   ├── view.py          # View 類別
│   ├── theme.py         # 主題系統
│   └── [150+ 模組]      # 各式 UI 元件
├── ads/                 # 廣告模組
├── auth/                # 認證模組
├── canvas/              # 畫布
├── map/                 # 地圖
├── security/            # 安全
└── utils/               # 工具函數
```

### 1.2 主要函數與簽名

#### `flet.app.app()` — 同步啟動應用程式

```python
def app(
    target,                      # 應用程式入口函數 (Callable)
    name: str = "",              # 應用程式名稱
    host: str = None,            # 主機位址
    port: int = 0,               # 連接埠（0 = 自動分配）
    view: Optional[AppView] = AppView.FLET_APP,  # 視圖類型
    assets_dir: str = "assets",  # 靜態資源目錄
    upload_dir = None,           # 上傳目錄
    web_renderer: WebRenderer = WebRenderer.CANVAS_KIT,
    use_color_emoji: bool = False,
    route_url_strategy: str = "path",
    export_asgi_app: bool = False,  # 匯出為 ASGI 應用
):
```

**重要特性**：
- 預設使用 `FLET_APP` 視圖，會開啟獨立的 Flet 客戶端視窗
- `export_asgi_app=True` 可匯出為 FastAPI ASGI 應用
- 支援環境變數覆蓋：`FLET_SERVER_PORT`, `FLET_SERVER_IP`, `FLET_ASSETS_DIR`

#### `flet.app.app_async()` — 異步啟動應用程式

```python
async def app_async(
    target,                      # 應用程式入口函數
    name: str = "",
    host: str = None,
    port: int = 0,
    view: Optional[AppView] = AppView.FLET_APP,
    assets_dir: str = "assets",
    upload_dir = None,
    web_renderer: WebRenderer = WebRenderer.CANVAS_KIT,
    use_color_emoji: bool = False,
    route_url_strategy: str = "path",
):
```

**視圖類型（AppView 列舉）**：
- `FLET_APP` — 開啟 Flet 桌面客戶端
- `FLET_APP_HIDDEN` — 隱藏啟動
- `FLET_APP_WEB` — Web 嵌入式
- `WEB_BROWSER` — 自動開啟瀏覽器

### 1.3 核心類別

#### `Page` — 頁面物件

```python
class Page:
    def __init__(
        self,
        connection,
        session_id: str,
        executor: ThreadPoolExecutor = None,
        loop: asyncio.AbstractEventLoop = None,
    ):
```

**重要屬性與方法**：
- `page.client_storage` — 客戶端儲存
- `page.session_storage` — 對話儲存
- `page.pubsub` — 發布/訂閱
- `page.route` — 路由
- `page.views` — 視圖堆疊
- `page.theme_mode` — 主題模式（light/dark/system）
- `page.go(route: str)` — 導航

**重要事件**：
- `on_route_change` — 路由變更
- `on_view_pop` — 視圖彈出
- `on_window_event` — 視窗事件

#### `Control` — UI 元件基底類別

所有 UI 元件都繼承自 `Control`，重要屬性：
- `visible`, `disabled`, `opacity`
- `margin`, `padding`
- `alignment`
- `expand`, `col`, `width`, `height`

### 1.4 主題系統

```python
from flet import Theme, ThemeMode

page.theme_mode = ThemeMode.DARK
page.theme = Theme(
    color_scheme_seed="blue",
    # ... 其他主題設定
)
```

---

## 2. flet_cli（命令列工具）

### 2.1 模組結構

```
flet_cli/
├── __init__.py
├── cli.py              # 主 CLI 入口
├── version.py
├── commands/
│   ├── base.py         # BaseCommand 抽象類別
│   ├── create.py       # 建立新專案
│   ├── run.py         # 執行開發伺服器
│   ├── build.py       # 建置發布版本（最大，82KB）
│   ├── pack.py        # 打包
│   ├── publish.py     # 發布
│   ├── doctor.py      # 診斷
│   └── options.py     # 共用選項
└── utils/
```

### 2.2 CLI 子命令

| 命令 | 說明 |
|------|------|
| `flet create` | 建立新 Flet 專案 |
| `flet run` | 執行開發伺服器（**預設子命令**） |
| `flet build` | 建置為 Web/桌面/AppImage/deb/rpm/macOS/Windows |
| `flet pack` | 打包為可執行檔 |
| `flet publish` | 發布到 Flet 雲端 |
| `flet doctor` | 診斷環境問題 |

### 2.3 CLI 入口點

```python
# flet_cli/cli.py
def main():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest="command")
    
    # 註冊子命令
    flet_cli.commands.create.Command.register_to(sp, "create")
    flet_cli.commands.run.Command.register_to(sp, "run")
    flet_cli.commands.build.Command.register_to(sp, "build")
    # ... 其他
    
    # 設定預設子命令為 "run"
    set_default_subparser(parser, name="run", index=1)
```

**使用範例**：
```bash
flet create my_app
flet run                    # 預設
flet run --port 5000
flet build web
flet build macos
flet build windows
```

### 2.4 BaseCommand 抽象類別

```python
class BaseCommand:
    name: Optional[str] = None          # 子命令名稱
    description: Optional[str] = None   # 說明文字
    arguments: List[Option] = [verbose_option]
    
    @classmethod
    def register_to(cls, subparsers, name=None, **kwargs):
        """註冊子命令"""
        
    def handle(self, options: argparse.Namespace) -> None:
        """命令處理函數"""
        raise NotImplementedError
```

---

## 3. flet_desktop（桌面客戶端）

### 3.1 模組結構

```
flet_desktop/
├── __init__.py          # 主要邏輯
├── version.py
└── app/                 # 應用程式碼
```

### 3.2 主要函數

#### `open_flet_view()` — 開啟 Flet 視圖（同步）

```python
def open_flet_view(page_url, assets_dir, hidden):
    """
    開啟 Flet 桌面客戶端視窗
    
    Parameters:
        page_url (str): 頁面 URL
        assets_dir (str): 靜態資源目錄
        hidden (bool): 是否隱藏啟動
    Returns:
        subprocess.Popen, pid_file
    """
```

#### `open_flet_view_async()` — 開啟 Flet 視圖（異步）

```python
async def open_flet_view_async(page_url, assets_dir, hidden):
    """異步版本"""
```

#### `close_flet_view()` — 關閉 Flet 視圖

```python
def close_flet_view(pid_file):
    """殺死 Flet View 程序並刪除 PID 檔案"""
```

### 3.3 客戶端下載邏輯

**運作流程**：
1. 先檢查 `build/windows`（本機建置）
2. 再檢查 `~/.flet/bin/flet-{version}/flet.exe`
3. 最後從 GitHub Releases 下載：
   ```python
   flet_url = f"https://github.com/flet-dev/flet/releases/download/v{ver}/{file_name}"
   ```

**下載的檔案**：
- Windows: `flet-windows.zip`
- macOS: `flet-macos.tar.gz`
- Linux: `flet-linux-{arch}.tar.gz`

### 3.4 環境變數

| 環境變數 | 說明 |
|----------|------|
| `FLET_VIEW_PATH` | 指定自訂 Flet 客戶端路徑（開發者模式） |

---

## 4. flet_web（Web 伺服器）

### 4.1 模組結構

```
flet_web/
├── __init__.py
├── version.py
├── patch_index.py       # HTML 修補
├── uploads.py           # 上傳處理
├── web/                 # 靜態 web 資源
└── fastapi/             # FastAPI 伺服器
    ├── app.py
    ├── flet_app.py           # FletApp 類別（核心）
    ├── flet_app_manager.py   # 應用程式管理器
    ├── flet_fastapi.py       # FastAPI 整合
    ├── flet_oauth.py         # OAuth 支援
    ├── flet_static_files.py  # 靜態檔案
    ├── flet_upload.py        # 上傳端點
    ├── serve_fastapi_web_app.py
    └── oauth_state.py
```

### 4.2 主要類別

#### `FletApp` — WebSocket 應用程式

```python
class FletApp(LocalConnection):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        session_handler,              # 對話處理函數
        session_timeout_seconds: int = 3600,      # 對話超時（預設 1 小時）
        oauth_state_timeout_seconds: int = 600,  # OAuth 狀態超時（預設 10 分鐘）
        upload_endpoint_path: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
```

**重要方法**：
- `await handle(websocket: WebSocket)` — 處理 WebSocket 連線

### 4.3 整合方式

#### 方式一：使用 `flet.app()` 自動

```python
import flet

def main(page):
    page.add("Hello")

flet.app(target=main)  # 自動啟動 web 伺服器
```

#### 方式二：使用 FastAPI 整合

```python
from flet_fastapi import FletApp
from fastapi import FastAPI

app = FastAPI()
flet_app = FletApp(session_handler=main)
app.mount("/", flet_app)
```

### 4.4 環境變數

| 環境變數 | 說明 |
|----------|------|
| `FLET_WEB_PATH` | 指定自訂 web 資源路徑 |
| `FLET_SESSION_TIMEOUT` | 對話超時（秒） |
| `FLET_OAUTH_STATE_TIMEOUT` | OAuth 狀態超時（秒） |

---

## 5. 重要 API 用法差異（與模型記憶不同）

### 5.1 app() vs app_async()

```python
# 同步版本（常用）
import flet
flet.app(target=main)

# 異步版本（需要 async def main）
import flet
await flet.app_async(target=main_async)
```

### 5.2 view 參數預設行為

**重要**：`view=AppView.FLET_APP` 預設會開啟獨立桌面視窗，而非瀏覽器！

若要在瀏覽器執行：
```python
flet.app(target=main, view=flet.AppView.WEB_BROWSER)
# 或設定環境變數
# FLET_FORCE_WEB_SERVER=true
```

### 5.3 assets_dir 路徑解析

```python
# 相對於目前工作目錄（CWD）
flet.app(target=main, assets_dir="assets")

# 或使用絕對路徑
flet.app(target=main, assets_dir="C:/path/to/assets")
```

### 5.4 Web 渲染器

```python
from flet.core.types import WebRenderer

# 預設使用 Canvas Kit（高效能）
web_renderer=WebRenderer.CANVAS_KIT

# 或使用 HTML（較少功能但更相容）
web_renderer=WebRenderer.HTML
```

### 5.5 PubSub 用法

```python
# 發布
page.pubsub.send_all("topic_name", "message")

# 訂閱（需要有 on_initialize 的協助類）
def main(page):
    def on_message(msg):
        print(msg)
    page.pubsub.subscribe_topic("topic_name", on_message)
```

---

## 6. 快速參考表

| 功能 | API |
|------|-----|
| 建立應用 | `flet.app(target=main)` |
| 頁面物件 | `page = Page(connection, session_id)` |
| 新增元件 | `page.add(control)` |
| 更新元件 | `page.update(control)` |
| 導航 | `page.go("/route")` |
| 主題 | `page.theme_mode = ThemeMode.DARK` |
| 客戶端儲存 | `page.client_storage` |
| 對話儲存 | `page.session_storage` |
| CLI 建置 | `flet build web` |
| CLI 執行 | `flet run` |

---

## 7. 外部資源

- GitHub: https://github.com/flet-dev/flet
- 文件: https://flet.dev/docs/
- Releases: https://github.com/flet-dev/flet/releases

---

*筆記結束*
