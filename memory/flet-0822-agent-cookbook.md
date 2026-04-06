# Flet 0.82.2 Cookbook（繁體中文）

> **版本標籤**：`flet:0.82.2`
> **資料來源**：https://docs.flet.dev/cookbook/
> **翻譯語言**：繁體中文
> **最後更新**：2026-03-22

---

## 目錄

1. [Accessibility（無障礙設計）](#1-accessibility無障礙設計)
2. [Adaptive Apps（自適應應用）](#2-adaptive-apps自適應應用)
3. [Animations（動畫）](#3-animations動畫)
4. [Assets（資源檔案）](#4-assets資源檔案)
5. [Async Apps（非同步應用）](#5-async-apps非同步應用)
6. [Authentication（認證）](#6-authentication認證)
7. [Client Storage（客戶端儲存）](#7-client-storage客戶端儲存)
8. [Colors（顏色）](#8-colors顏色)
9. [Control Refs（控制項引用）](#9-control-refs控制項引用)
10. [Custom Controls（自訂控制項）](#10-custom-controls自訂控制項)
11. [Drag and Drop（拖放）](#11-drag-and-drop拖放)
12. [Encrypting Sensitive Data（加密敏感資料）](#12-encrypting-sensitive-data加密敏感資料)
13. [Expanding Controls（展開控制項）](#13-expanding-controls展開控制項)
14. [Fonts（字體）](#14-fonts字體)
15. [Keyboard Shortcuts（鍵盤快捷鍵）](#15-keyboard-shortcuts鍵盤快捷鍵)
16. [Large Lists（大型列表）](#16-large-lists大型列表)
17. [Pubsub（發布訂閱）](#17-pubsub發布訂閱) ✅
18. [Read and Write Files（檔案讀寫）](#18-read-and-write-files檔案讀寫)
19. [Session Storage（工作階段儲存）](#19-session-storage工作階段儲存)
20. [Subprocess（子程序）](#20-subprocess子程序)
21. [Theming（主題）](#21-theming主題)

---

## 1. Accessibility（無障礙設計）

**核心概念**：Flet 基於 Flutter，內建無障礙支援。行動裝置透過 TalkBack/VoiceOver 語音回饋；桌面瀏覽器支援 JAWs、NVDA、VoiceOver。Web 版需點擊「Enable accessibility」按鈕建構語義樹。

**關鍵 API**：
- `Text.semantics_label` — 覆寫預設語義標籤
- `TextField.label`、`Dropdown.label` — 為表單控制項添加螢幕閱讀器標籤
- `Semantics` 控制項 — 自訂語義
- `Page.show_semantics_debugger` — 顯示除錯疊加層
- IconButton / FloatingActionButton / PopupMenuButton 的 `tooltip` 屬性

**最小範例**（Shift+S 切換語義除錯器）：

```python
import flet as ft

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def on_keyboard(e: ft.KeyboardEvent):
        if e.shift and e.key == "S":
            page.show_semantics_debugger = not page.show_semantics_debugger
            page.update()

    page.on_keyboard_event = on_keyboard

    def button_click(e: ft.Event[ft.Button]):
        counter.value = str(int(counter.value) + 1)
        page.update()

    page.add(
        counter := ft.Text("0", size=40),
        ft.Text("Press Shift+S to toggle semantics debugger"),
        ft.Button(
            content="Increment number",
            icon=ft.Icons.ADD,
            on_click=button_click,
        ),
    )

ft.run(main)
```

---

## 2. Adaptive Apps（自適應應用）

**核心概念**：單一程式碼基底根據裝置平台自動調整外觀。設 `page.adaptive = True` 即可讓整個應用程式在 iOS 和 Android 上呈現原生樣式。

**關鍵 API**：
- `Page.adaptive` — 全域自適應模式
- `Control.adaptive` — 單一控制項自適應
- 容器設定 `adaptive=True` 時，所有子控制項也會跟著自適應（可被子層覆寫）
- `Page.platform` — 偵測平台（iOS/macOS → Cupertino，否則 → Material）
- Cupertino 控制項：`CupertinoAlertDialog`、`CupertinoNavigationBar`、`CupertinoTextField`、`CupertinoSwitch`、`CupertinoSlider`、`CupertinoCheckbox` 等
- Material 控制項的 `adaptive=True` 屬性，會依平台自動切換為對應 Cupertino 控制項

**最小範例**：

```python
import flet as ft

def main(page):
    page.adaptive = True
    page.appbar = ft.AppBar(
        leading=ft.TextButton("New", style=ft.ButtonStyle(padding=0)),
        title=ft.Text("Adaptive AppBar"),
        actions=[
            ft.IconButton(ft.cupertino_icons.ADD, style=ft.ButtonStyle(padding=0))
        ],
        bgcolor=ft.Colors.with_opacity(0.04, ft.CupertinoColors.SYSTEM_BACKGROUND),
    )
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explore"),
            ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label="Commute"),
            ft.NavigationBarDestination(
                icon=ft.Icons.BOOKMARK_BORDER,
                selected_icon=ft.Icons.BOOKMARK,
                label="Bookmark",
            ),
        ],
    )
    page.add(ft.SafeArea(ft.Column([
        ft.Checkbox(value=False, label="Dark Mode"),
        ft.Text("First field:"),
        ft.TextField(keyboard_type=ft.KeyboardType.TEXT),
        ft.Text("Second field:"),
        ft.TextField(keyboard_type=ft.KeyboardType.TEXT),
        ft.Switch(label="A switch"),
        ft.FilledButton(content=ft.Text("Adaptive button")),
    ])))

ft.run(main)
```

---

## 3. Animations（動畫）

**核心概念**：隱式動畫（Implicit Animations）透過設定目標值，讓控制項屬性變化時自動產生內插動畫。可套用曲線（curve）改變緩動效果。

**關鍵 API**（`LayoutControl` 及其子類）：
- `animate_opacity` — 透明度動畫
- `animate_rotation` — 旋轉動畫
- `animate_scale` — 縮放動畫
- `animate_offset` — 位移動畫（Stack 或 Page.overlay 中有效）
- `animate_position` — 位置動畫（`left`、`right`、`bottom`、`top`）
- `animate`（Container）— 通用動畫
- 可設值：`True`（預設 1000ms LINEAR）、整數（毫秒）、`Animation(duration, curve)`

**AnimationCurve**：`LINEAR`、`EASE_OUT_CUBIC`、`BOUNCE_OUT` 等

**最小範例**（縮放動畫）：

```python
import flet as ft

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.spacing = 30

    def animate(e: ft.Event[ft.Button]):
        container.scale = 2 if container.scale == 1 else 1
        page.update()

    page.add(
        container := ft.Container(
            width=100, height=100,
            bgcolor=ft.Colors.BLUE,
            border_radius=5,
            scale=1,
            animate_scale=ft.Animation(
                duration=600,
                curve=ft.AnimationCurve.BOUNCE_OUT,
            ),
        ),
        ft.Button("Animate!", on_click=animate),
    )

ft.run(main)
```

**Offset 動畫範例**（滑入效果）：

```python
import flet as ft

def main(page: ft.Page):
    def animate(e: ft.Event[ft.Button]):
        container.offset = ft.Offset(0, 0)
        container.update()

    page.add(
        container := ft.Container(
            width=150, height=150,
            bgcolor=ft.Colors.BLUE,
            border_radius=ft.BorderRadius.all(10),
            offset=ft.Offset(x=-1.1, y=0),
            animate_offset=ft.Animation(
                duration=600,
                curve=ft.AnimationCurve.BOUNCE_OUT,
            ),
        ),
        ft.Button("Reveal!", on_click=animate),
    )

ft.run(main)
```

---

## 4. Assets（資源檔案）

**核心概念**：Flet 應用可打包圖片、字體、JSON、設定檔等資源。透過 `ft.run(assets_dir="assets")` 指定資源目錄。`FLET_ASSETS_DIR` 環境變數在正式版中會是絕對路徑。

**關鍵 API**：
- `ft.run(assets_dir="assets")` — 指定資源目錄（相對於入口檔或絕對路徑）
- `FLET_ASSETS_DIR` 環境變數 — 正式版資源目錄的絕對路徑
- `Image(src="images/sample.png")` — UI 控制項直接用相對路徑

**最小範例**（顯示本地圖片）：

```
📁 assets
└── 📁 images
    └── sample.png
main.py
```

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Image(src="images/sample.png"))

ft.run(main, assets_dir="assets")
```

**讀取非 UI 資源（正式版相容）**：

```python
import json, os
from pathlib import Path

def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()

def main(page: ft.Page):
    assets_dir = get_assets_dir()
    with (assets_dir / "data" / "some_config.json").open() as f:
        config = json.load(f)
    page.add(ft.Text(f"Loaded profile: {config['profile_name']}"))

ft.run(main, assets_dir="assets")
```

---

## 5. Async Apps（非同步應用）

**核心概念**：Flet 支援 async/await，可將 `main()` 設為 async，並在事件處理常式中使用 coroutine。適用於需要 concurrency 而非平行 threading 的場景（如 Pyodide/WASM 環境不支援執行緒）。

**關鍵 API**：
- `async def main(page: ft.Page)` — async 主函式
- `ft.run(main)` — 自動偵測 async
- `await ft.run_async(main)` — 從其他 async 程式碼呼叫 Flet 應用
- `page.run_task()` — 在背景執行任務
- `asyncio.sleep()` 而非 `time.sleep()`

**最小範例**：

```python
import flet as ft

async def main(page: ft.Page):
    await asyncio.sleep(1)
    page.add(ft.Text("Hello, async world!"))

ft.run(main)
```

**背景倒數計時範例**（使用 `run_task`）：

```python
import asyncio
import flet as ft

class Countdown(ft.Text):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_timer)

    def will_unmount(self):
        self.running = False

    async def update_timer(self):
        while self.seconds and self.running:
            mins, secs = divmod(self.seconds, 60)
            self.value = "{:02d}:{:02d}".format(mins, secs)
            self.update()
            await asyncio.sleep(1)
            self.seconds -= 1

def main(page: ft.Page):
    page.add(Countdown(120), Countdown(60))

ft.run(main)
```

---

## 6. Authentication（認證）

**核心概念**：透過 OAuth 2.0 Authorization Code Flow 支援第三方登入（GitHub、Google、Azure、Auth0）。需向 OAuth provider 註冊應用程式，取得 Client ID 與 Client Secret，設定 callback URL。

**關鍵 API**：
- `GitHubOAuthProvider`、`GoogleOAuthProvider`、`AzureOAuthProvider`、`Auth0OAuthProvider`
- `page.login(provider)` — 觸發 OAuth 流程
- `page.on_login` — 登入成功/失敗事件（`LoginEvent.error`、`page.auth.token`、`page.auth.user`）
- `page.auth.token.to_json()` — 序列化權杖供儲存
- 內建 scope：`fetch_user`、`fetch_groups`、`scope`

**最小範例**（GitHub 登入）：

```python
import os
import flet as ft
from flet.auth.providers import GitHubOAuthProvider

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

def main(page: ft.Page):
    provider = GitHubOAuthProvider(
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        redirect_url="http://localhost:8550/oauth_callback",
    )

    def login_click(e):
        page.login(provider)

    def on_login(e):
        print("Login error:", e.error)
        print("Access token:", page.auth.token.access_token)
        print("User ID:", page.auth.user.id)

    page.on_login = on_login
    page.add(ft.Button("Login with GitHub", on_click=login_click))

ft.run(main, port=8550, view=ft.WEB_BROWSER)
```

> **⚠️ 安全注意**：嚴禁將 Client Secret 寫入原始碼，應使用環境變數。

---

## 7. Client Storage（客戶端儲存）

**核心概念**：跨平台的鍵值儲存 API。底層依平台使用 LocalStorage（Web）、JSON 檔（Desktop）、NSUserDefaults（iOS）、SharedPreferences（Android）。**注意**：所有 Flet 應用共享同一組 preferences，建議用 `{company}.{product}` 前綴區分。

**關鍵 API**：
- `page.shared_preferences.set(key, value)` — 寫入（支援 str、int、bool、list）
- `page.shared_preferences.get(key)` — 讀取（自動轉回原類型）
- `page.shared_preferences.contains_key(key)` — 檢查鍵是否存在
- `page.shared_preferences.get_keys("prefix.")` — 前綴查詢所有鍵
- `page.shared_preferences.remove(key)` — 刪除單一鍵
- `page.shared_preferences.clear()` — **⚠️ 清除所有 Flet 應用的所有資料**

> **⚠️ 安全注意**：敏感資料應先加密再存入 client storage。

**最小範例**：

```python
# 寫入
await page.shared_preferences.set("key", "value")
await page.shared_preferences.set("number.setting", 12345)
await page.shared_preferences.set("bool_setting", True)
await page.shared_preferences.set("favorite_colors", ["red", "green", "blue"])

# 讀取
value = await page.shared_preferences.get("key")
colors = await page.shared_preferences.get("favorite_colors")  # ["red", "green", "blue"]

# 檢查與刪除
await page.shared_preferences.contains_key("key")
await page.shared_preferences.remove("key")
```

---

## 8. Colors（顏色）

**核心概念**：支援 Hex 色碼（`#rrggbb` 或 `#aarrggbb`）與 Material Design 命名顏色。Theme colors 由 `color_scheme_seed` 自動生成 30 種色階。Color palettes 提供從 50 到 900 的完整色階。

**關鍵 API**：
- Hex：`ft.Container(bgcolor="#ff0000")` 或 `bgcolor=0xff0000ff`
- `ft.Colors.YELLOW`、`ft.CupertinoColors.DESTRUCTIVE_RED`
- `ft.Colors.with_opacity(0.5, ft.Colors.RED)` → `"red,0.5"`
- `page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)` — 設定主題 seed
- `ft.ColorScheme(primary=..., error=...)` — 覆寫特定色階
- 三層級顏色覆寫：Control 層 > Control Theme 層 > Ancestor Theme 層

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.GREEN,
            error=ft.Colors.RED,
        ),
    )
    page.add(ft.Card(bgcolor=ft.Colors.GREEN_200))
    page.add(
        ft.Container(
            width=200, height=200,
            border=ft.border.all(1, ft.Colors.BLACK),
            content=ft.FilledButton("Primary color"),
            theme=ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.YELLOW))
        )
    )

ft.run(main)
```

---

## 9. Control Refs（控制項引用）

**核心概念**：Flet 控制項是物件，需透過變數持有參考。`Ref[T]()` 類別借鑒 React，先定義參考，之後再賦值給實際控制項，讓 `page.add()` 的結構更清晰。

**關鍵 API**：
- `ft.Ref[ft.TextField]()` — 定義強型別參考
- `ref.current` — 解參考（取得實際控制項）
- `Control.ref = ref` — 將控制項指派給參考

**最小範例**：

```python
import flet as ft

def main(page):
    first_name = ft.Ref[ft.TextField]()
    last_name = ft.Ref[ft.TextField]()
    greetings = ft.Ref[ft.Column]()

    async def btn_click(e):
        greetings.current.controls.append(
            ft.Text(f"Hello, {first_name.current.value} {last_name.current.value}!")
        )
        first_name.current.value = ""
        last_name.current.value = ""
        page.update()
        await first_name.current.focus()

    page.add(
        ft.TextField(ref=first_name, label="First name", autofocus=True),
        ft.TextField(ref=last_name, label="Last name"),
        ft.Button("Say hello!", on_click=btn_click),
        ft.Column(ref=greetings),
    )

ft.run(main)
```

---

## 10. Custom Controls（自訂控制項）

**核心概念**：透過 Python OOP 繼承 Flet 控制項，建立可複用的樣式化或複合控制項。可用 `@dataclass` 或 `@ft.control` 裝飾器。

**關鍵 API**：
- `@ft.control`（或 `@dataclass`）— 定義自訂控制項
- `ft.control` 的 `init()` 方法 — 初始化（可對映屬性）
- 生命週期方法：`build()`（控制項建立時）、`did_mount()`（加入頁面後）、`will_unmount()`（移除前）、`before_update()`（更新前）
- 子類可為 Column、Row、Stack、Container 等容器

**Styled Control 範例**：

```python
import flet as ft
from dataclasses import field

@ft.control
class MyButton(ft.Button):
    bgcolor: ft.Colors = ft.Colors.ORANGE_300
    color: ft.Colors = ft.Colors.GREEN_800
    style: ft.ButtonStyle = field(
        default_factory=lambda: ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )
    expand: int = 1
```

**Composite Control 範例**（可編輯的 Task）：

```python
import flet as ft

@ft.control
class Task(ft.Row):
    text: str = ""

    def init(self):
        self.text_view = ft.Text(value=self.text)
        self.text_edit = ft.TextField(value=self.text, visible=False)
        self.edit_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=self.edit)
        self.save_button = ft.IconButton(
            visible=False, icon=ft.Icons.SAVE, on_click=self.save
        )
        self.controls = [
            ft.Checkbox(),
            self.text_view,
            self.text_edit,
            self.edit_button,
            self.save_button,
        ]

    def edit(self, e):
        self.edit_button.visible = False
        self.save_button.visible = True
        self.text_view.visible = False
        self.text_edit.visible = True
        self.update()

    def save(self, e):
        self.edit_button.visible = True
        self.save_button.visible = False
        self.text_view.visible = True
        self.text_edit.visible = False
        self.text_view.value = self.text_edit.value
        self.update()

def main(page: ft.Page):
    page.add(Task(text="Do laundry"), Task(text="Cook dinner"))

ft.run(main)
```

---

## 11. Drag and Drop（拖放）

**核心概念**：`Draggable` 拖動 `DragTarget`，兩者需有相同的 `group` 才會觸發 `on_accept`。拖動來源可透過 `page.get_control(e.src_id)` 取得。

**關鍵 API**：
- `Draggable(group="number", content=..., content_when_dragging=..., content_feedback=...)`
- `DragTarget(group="number", on_accept=..., on_will_accept=..., on_leave=...)`
- `e.src_id` — 取得拖動來源的 control ID
- `page.get_control(id)` — 以 ID 取得控制項

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Drag and Drop example"

    def drag_accept(e):
        src = page.get_control(e.src_id)
        src.content.content.value = "0"
        e.control.content.content.value = "1"
        page.update()

    page.add(
        ft.Row([
            ft.Draggable(
                group="number",
                content=ft.Container(
                    width=50, height=50,
                    bgcolor=ft.Colors.CYAN_200,
                    border_radius=5,
                    content=ft.Text("1", size=20),
                    alignment=ft.alignment.center,
                ),
            ),
            ft.Container(width=100),
            ft.DragTarget(
                group="number",
                content=ft.Container(
                    width=50, height=50,
                    bgcolor=ft.Colors.PINK_200,
                    border_radius=5,
                    content=ft.Text("0", size=20),
                    alignment=ft.alignment.center,
                ),
                on_accept=drag_accept,
            ),
        ])
    )

ft.run(main)
```

**進階（拖動視覺回饋 + 目標高亮）**：

```python
# 在 Draggable 中加入：
content_when_dragging=ft.Container(width=50, height=50, bgcolor=ft.Colors.BLUE_GREY_200, border_radius=5),
content_feedback=ft.Text("1"),

# 在 DragTarget 中加入：
on_will_accept=drag_will_accept,
on_leave=drag_leave,

# 其中：
def drag_will_accept(e):
    e.control.content.border = ft.border.all(
        2, ft.Colors.BLACK_45 if e.data == "true" else ft.Colors.RED
    )
    e.control.update()

def drag_leave(e):
    e.control.content.border = None
    e.control.update()
```

---

## 12. Encrypting Sensitive Data（加密敏感資料）

**核心概念**：使用 Fernet（AES 128 + PBKDF2）對稱加密。`encrypt()` / `decrypt()` 來自 `flet.security`。密鑰（passphrase）由使用者提供，演算法從中衍生 32 位元金鑰。

**關鍵 API**：
- `from flet.security import encrypt, decrypt`
- `encrypt(plain_text, secret_key)` — 加密（僅接受字串）
- `decrypt(encrypted_data, secret_key)` — 解密
- 環境變數 `MY_APP_SECRET_KEY` 存放密鑰

> **⚠️ 安全注意**：嚴禁將密鑰寫入原始碼；加密前需先將物件序列化（JSON/XML）。

**最小範例**：

```python
import os
from flet.security import encrypt, decrypt

secret_key = os.getenv("MY_APP_SECRET_KEY")

# 加密
plain_text = "This is a secret message!"
encrypted_data = encrypt(plain_text, secret_key)

# 解密
plain_text = decrypt(encrypted_data, secret_key)
print(plain_text)
```

---

## 13. Expanding Controls（展開控制項）

**核心概念**：`Row`、`Column`、`View`、`Page` 中的子控制項可設 `expand` 屬性來佔據可用空間。`expand=True` 佔全部；`expand=整數` 按比例分配（1+3+1 表示 20%/60%/20%）。`expand_loose` 則是彈性展開（可選擇不佔滿）。

**關鍵 API**：
- `expand=True`（布林）— 佔全部可用空間
- `expand=整數` — 按比例分配剩餘空間
- `expand_loose` — 彈性展開，可選是否填滿

**最小範例**（TextField 填滿剩餘空間）：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Container(
            width=480, padding=10,
            border=ft.Border.all(2, ft.Colors.BLUE_GREY_200),
            border_radius=10,
            content=ft.Row([
                ft.TextField(hint_text="Enter your name", expand=True),
                ft.Button("Join chat"),
            ]),
        )
    )

ft.run(main)
```

**比例分配（1:3:1）**：

```python
content=ft.Row([
    ft.Container(expand=1, height=60, bgcolor=ft.Colors.CYAN_300, content=ft.Text("1")),
    ft.Container(expand=3, height=60, bgcolor=ft.Colors.AMBER_300, content=ft.Text("3")),
    ft.Container(expand=1, height=60, bgcolor=ft.Colors.PINK_200, content=ft.Text("1")),
])
```

---

## 14. Fonts（字體）

**核心概念**：可使用系統已安裝字體，或從外部 URL / 專案 assets 目錄載入字體。需設定 `page.fonts` 並透過 `Theme.font_family` 或個別 `Text.font_family` 指定。

**關鍵 API**：
- `page.fonts = {"FontName": "path_or_url"}` — 註冊字體
- `Theme.font_family` — 全域預設字體
- `Text.font_family` — 單一文字控制項字體
- 目前僅支援 Static Fonts；Variable Fonts 可用 fonttools 工具預先產生靜態實例

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
        "Open Sans": "/fonts/OpenSans-Regular.ttf"
    }
    page.theme = ft.Theme(font_family="Kanit")  # 預設字體
    page.add(
        ft.Text("This text uses the Kanit font"),
        ft.Text("This text uses the Open Sans font", font_family="Open Sans")
    )

ft.run(main, assets_dir="assets")
```

> **⚠️ 限制**：系統字體無法用於 canvas kit Web 渲染器。

---

## 15. Keyboard Shortcuts（鍵盤快捷鍵）

**核心概念**：透過 `page.on_keyboard_event` 處理全域鍵盤事件。`KeyboardEvent` 包含 `key`、`shift`、`ctrl`、`alt`、`meta` 等屬性。

**關鍵 API**：
- `page.on_keyboard_event` — 全域鍵盤事件處理常式
- `KeyboardEvent.key` — 按鍵文字表示（如 "A"、"Enter"、"F5"）
- `KeyboardEvent.shift/ctrl/alt/meta` — 修飾鍵布林值

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    def on_keyboard(e: ft.KeyboardEvent):
        page.add(
            ft.Text(
                f"Key: {e.key}, Shift: {e.shift}, Control: {e.ctrl}, "
                f"Alt: {e.alt}, Meta: {e.meta}"
            )
        )

    page.on_keyboard_event = on_keyboard
    page.add(ft.Text("Press any key with CTRL/ALT/SHIFT/META..."))

ft.run(main)
```

---

## 16. Large Lists（大型列表）

**核心概念**：超過數百到數千項的列表，嚴禁使用 `Column`/`Row`（會一次渲染全部），應改用 `ListView` 或 `GridView`（按需渲染）。大量控制項應批次更新（batch updates）。

**關鍵 API**：
- `ListView(expand=True, spacing=10, item_extent=50)` — 垂直/水平滾動列表
- `GridView(expand=True, max_extent=150, child_aspect_ratio=1)` — 網格視圖
- `item_extent` 或 `first_item_prototype=True` — 固定高度提升效能
- `FLET_WS_MAX_MESSAGE_SIZE` — WebSocket 訊息大小限制（預設 1MB）
- 批次更新：`if i % 500 == 0: page.update()`

**ListView 範例**（5000 項目）：

```python
import flet as ft

def main(page: ft.Page):
    lv = ft.ListView(expand=True, spacing=10, item_extent=50)
    for i in range(5000):
        lv.controls.append(ft.Text(f"Line {i}"))
    page.add(lv)

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

**批次更新**：

```python
lv = ft.ListView(expand=1, spacing=10, item_extent=50)
page.add(lv)
for i in range(5100):
    lv.controls.append(ft.Text(f"Line {i}"))
    if i % 500 == 0:
        page.update()
page.update()  # 最後一批
```

---

## 17. Pubsub（發布訂閱）

**核心概念**：Flet 內建 PubSub 機制，支援跨 session 的非同步訊息廣播。適用於聊天應用、多人即時協作等場景。

**關鍵 API**：
- `page.pubsub.subscribe(on_message)` — 訂閱廣播訊息
- `page.pubsub.subscribe_topic(topic_name, handler)` — 訂閱特定主題頻道
- `page.pubsub.send_all(message)` — 向所有 session 廣播訊息
- `page.pubsub.send_all_on_topic(topic, message)` — 發送訊息到特定主題
- `page.pubsub.unsubscribe()` — 取消訂閱
- `page.pubsub.unsubscribe_topic(topic)` — 取消特定主題訂閱
- `page.pubsub.unsubscribe_all()` — 取消所有訂閱（在 `page.on_close` 中使用）

**最小範例（簡易聊天應用）**：

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Flet Chat"

    def on_message(msg):
        messages.controls.append(ft.Text(msg))
        page.update()

    page.pubsub.subscribe(on_message)

    def send_click(e):
        page.pubsub.send_all(f"{user.value}: {message.value}")
        message.value = ""
        page.update()

    messages = ft.Column()
    user = ft.TextField(hint_text="Your name", width=150)
    message = ft.TextField(hint_text="Your message...", expand=True)
    send = ft.Button("Send", on_click=send_click)
    page.add(messages, ft.Row(controls=[user, message, send]))

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

**與 0.28.3 差異**：PubSub API 本身在 0.82.x 與 0.28.3 差異不大，核心用法相同。

---

## 18. Read and Write Files（檔案讀寫）

**核心概念**：使用 Python 內建的 `open()` 函式。Flet 提供兩個環境變數做為儲存路徑：`FLET_APP_STORAGE_DATA`（持久資料）和 `FLET_APP_STORAGE_TEMP`（暫存）。

**關鍵 API**：
- `FLET_APP_STORAGE_DATA` — 應用資料目錄（持久）
- `FLET_APP_STORAGE_TEMP` — 暫存目錄
- Python `open()`、`os` 模組

**最小範例**：

```python
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
my_file_path = os.path.join(app_data_path, "test_file.txt")

# 寫入
with open(my_file_path, "w") as f:
    f.write("Some file content...")

# 讀取
with open(my_file_path, "r") as f:
    print(f.read())
```

**計數器應用（跨啟動持久化）**：

```python
import os
import flet as ft

FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")
COUNTER_FILE_PATH = os.path.join(FLET_APP_STORAGE_DATA, "counter.txt")

class Counter(ft.Text):
    def __init__(self, storage_path=COUNTER_FILE_PATH):
        super().__init__(theme_style=ft.TextThemeStyle.HEADLINE_LARGE)
        self.storage_path = storage_path
        self.count = self._read()

    def increment(self):
        self.count += 1
        self.update()
        self._write()

    def _read(self):
        try:
            with open(self.storage_path, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _write(self):
        with open(self.storage_path, "w") as f:
            f.write(str(self.count))

def main(page: ft.Page):
    counter = Counter()
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, text="Increment Counter",
        on_click=lambda e: counter.increment(),
    )
    page.add(ft.SafeArea(counter))

ft.run(main)
```

---

## 19. Session Storage（工作階段儲存）

**核心概念**：Flet 提供伺服器端的鍵值儲存 API，存在使用者工作階段中。**注意**：目前實作中，工作階段資料不是持久化的，應用程式重啟後會消失。

**關鍵 API**：
- `page.session.store.set(key, value)` — 寫入（支援 str、int、bool、list）
- `page.session.store.get(key)` — 讀取（自動轉回原類型）
- `page.session.store.contains_key(key)` — 檢查鍵是否存在
- `page.session.store.get_keys()` — 取得所有鍵
- `page.session.store.remove(key)` — 刪除單一鍵
- `page.session.store.clear()` — 清除所有工作階段資料

**最小範例**：

```python
# 寫入
page.session.store.set("key", "value")
page.session.store.set("number.setting", 12345)
page.session.store.set("bool_setting", True)
page.session.store.set("favorite_colors", ["red", "green", "blue"])

# 讀取
value = page.session.store.get("key")
colors = page.session.store.get("favorite_colors")

# 檢查與刪除
page.session.store.contains_key("key")
page.session.store.remove("key")
page.session.store.clear()
```

---

## 20. Subprocess（子程序）

**核心概念**：使用 Python 內建 `subprocess` 模組在 Flet 應用中執行外部系統指令。適用於桌面/行動裝置呼叫平台工具或系統工具。**不支援瀏覽器環境**。

**關鍵 API**：
- `subprocess.run([args], shell=False, capture_output=True, text=True)` — 執行命令
- **⚠️** `shell=False` 時引數需為列表；`shell=True` 時需為單一字串

**最小範例**（Android 開啟設定應用）：

```python
import subprocess
import flet as ft

def main(page: ft.Page):
    def open_settings(e):
        result = subprocess.run(
            ["am", "start", "-n", "com.android.settings/.Settings", "--user", "0"],
            shell=False,
            capture_output=True,
            text=True,
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

    page.add(
        ft.SafeArea(
            content=ft.Button("Open Settings app", on_click=open_settings)
        )
    )

ft.run(main)
```

> **⚠️ 常見錯誤**：`shell=True` 時傳入列表，應改為單一字串或改用 `shell=False`。

---

## 21. Theming（主題）

**核心概念**：Flet 支援全域主題（Light/Dark）和巢狀主題。`Page.theme` 和 `Page.dark_theme` 設定整個應用的預設主題。容器（如 `Container`）可覆寫子樹的主題或色階。

**關鍵 API**：
- `page.theme` / `page.dark_theme` — 全域主題
- `Theme(color_scheme_seed=...)` — 以單一顏色生成完整色階
- `Theme(color_scheme=ColorScheme(primary=..., error=...))` — 覆寫特定色階
- `Container.theme` — 巢狀主題（覆寫繼承的父主題）
- `Container.theme_mode` — 設定獨立於父主題的模式（如固定 DARK）
- `ThemeMode.SYSTEM` / `ThemeMode.LIGHT` / `ThemeMode.DARK`

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    # 黃色頁面主題，SYSTEM 模式
    page.theme = ft.Theme(color_scheme_seed=ft.Colors
Colors.YELLOW)

    page.add(
        # Page theme
        ft.Container(
            content=ft.Button('Page theme button'),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
            width=300,
        ),
        # Inherited theme with primary color overridden
        ft.Container(
            theme=ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.PINK)),
            content=ft.Button('Inherited theme button'),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
            width=300,
        ),
        # Unique always DARK theme
        ft.Container(
            theme=ft.Theme(color_scheme_seed=ft.Colors.INDIGO),
            theme_mode=ft.ThemeMode.DARK,
            content=ft.Button('Unique theme button'),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
            width=300,
        ),
    )

ft.run(main)
