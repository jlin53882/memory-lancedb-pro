# Flet 0.82.2 Declarative vs Imperative 學習筆記

> **版本**：flet:0.82.2
> **來源**：https://docs.flet.dev/cookbook/declarative-vs-imperative-crud-app/
> **日期**：2026-03-22
> **重要度**：⭐⭐⭐⭐⭐（核心新範式）

---

## 一、兩種寫法的核心差異

| 面向 | Imperative（命令式） | Declarative（宣告式） |
|---|---|---|
| 思維 | **UI-first**：直接操作控制項 | **Model-first**：只操作狀態，UI 自動響應 |
| 控制項 | `self.controls.remove(...)` | 完全不操作 |
| 更新觸發 | 手動呼叫 `page.update()` | **自動**，靠 observable 監聽 |
| 複雜度 | 簡單 App 很直觀 | 複雜 App 更易維護 |
| 適合場景 | 簡單一次性 UI | 有多名稱/狀態的 App |

---

## 二、Declarative 三大核心概念

### 1. `@ft.observable` — 觀察物件（狀態的真相來源）

標記一個 dataclass 為「可觀察」：
```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class User:
    first_name: str
    last_name: str

    def update(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

@ft.observable
@dataclass
class App:
    users: list[User] = field(default_factory=list)

    def add_user(self, first_name: str, last_name: str):
        if first_name.strip() or last_name.strip():
            self.users.append(User(first_name, last_name))

    def delete_user(self, user: User):
        self.users.remove(user)
```

**效果**：賦值給 observable 的欄位時（例如 `user.first_name = "Ada"`），Flet 自動重新渲染有讀取該欄位的元件。**不需要手動呼叫 `page.update()`。**

### 2. `@ft.component` — 元件工廠（UI = f(state)）

標記一個函式為「元件」：
```python
@ft.component
def UserView(user: User, delete_user) -> ft.Control:
    # ...
    return ft.Row([...])
```

規則：
- 元件是**函式**，給定相同 state，每次返回相同 UI
- 元件**不直接操作 Page 樹**
- 元件props（引數）可以接收 observable 物件

### 3. `ft.use_state` — Hook（在地的、短期存在的 UI 狀態）

```python
count, set_count = ft.use_state(0)

ft.Button("+", on_click=lambda _: set_count(count + 1))
```

**什麼時候用：**
- **use_state**：在地 UI 狀態（開關、當前輸入值），**不需要持久化**
- **observable**：持久化的應用程式資料（真正要儲存的東西）

---

## 三、完整 Declarative CRUD 範例（User Manager）

```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class User:
    first_name: str
    last_name: str

    def update(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

@ft.observable
@dataclass
class App:
    users: list[User] = field(default_factory=list)

    def add_user(self, first_name: str, last_name: str):
        if first_name.strip() or last_name.strip():
            self.users.append(User(first_name, last_name))

    def delete_user(self, user: User):
        self.users.remove(user)

@ft.component
def UserView(user: User, delete_user) -> ft.Control:
    # 在地編輯狀態
    is_editing, set_is_editing = ft.use_state(False)
    new_first_name, set_new_first_name = ft.use_state(user.first_name)
    new_last_name, set_new_last_name = ft.use_state(user.last_name)

    def start_edit():
        set_new_first_name(user.first_name)
        set_new_last_name(user.last_name)
        set_is_editing(True)

    def save():
        user.update(new_first_name, new_last_name)
        set_is_editing(False)

    def cancel():
        set_is_editing(False)

    if not is_editing:
        return ft.Row([
            ft.Text(f"{user.first_name} {user.last_name}"),
            ft.Button("Edit", on_click=start_edit),
            ft.Button("Delete", on_click=lambda: delete_user(user)),
        ])

    return ft.Row([
        ft.TextField(
            label="First Name",
            value=new_first_name,
            on_change=lambda e: set_new_first_name(e.control.value),
            width=180,
        ),
        ft.TextField(
            label="Last Name",
            value=new_last_name,
            on_change=lambda e: set_new_last_name(e.control.value),
            width=180,
        ),
        ft.Button("Save", on_click=save),
        ft.Button("Cancel", on_click=cancel),
    ])

@ft.component
def AddUserForm(add_user) -> ft.Control:
    new_first_name, set_new_first_name = ft.use_state("")
    new_last_name, set_new_last_name = ft.use_state("")

    def add_user_and_clear():
        add_user(new_first_name, new_last_name)
        set_new_first_name("")
        set_new_last_name("")

    return ft.Row([
        ft.TextField(label="First Name", width=200, value=new_first_name,
                     on_change=lambda e: set_new_first_name(e.control.value)),
        ft.TextField(label="Last Name", width=200, value=new_last_name,
                     on_change=lambda e: set_new_last_name(e.control.value)),
        ft.Button("Add", on_click=add_user_and_clear),
    ])

@ft.component
def AppView() -> list[ft.Control]:
    app, _ = ft.use_state(
        App(users=[
            User("John", "Doe"),
            User("Jane", "Doe"),
            User("Foo", "Bar"),
        ])
    )
    return [
        AddUserForm(app.add_user),
        *[UserView(user, app.delete_user) for user in app.users],
    ]

ft.run(lambda page: page.render(AppView))
```

---

## 四、Rewrite Recipes（Imperative → Declarative）

### 1. 可見性開關 → 條件渲染

```python
# Imperative
self.text.visible = False
self.save_button.visible = True
self.page.update()

# Declarative
return (
    ft.Row([...read-only...])
    if not is_editing
    else ft.Row([...edit form...])
)
```

### 2. 直接操作控制項 → 操作模型

```python
# Imperative
self.text.value = f"{first} {last}"

# Declarative
user.update(new_first_name, new_last_name)
```

### 3. 到處呼叫 `page.update()` → 完全不需要

```python
# Imperative：每個 handler 都要
self.page.update()

# Declarative：完全不需要
# Flet 自動追蹤狀態改變並重新渲染
```

### 4. Handler 操作視圖 → Handler 只操作狀態

```python
# Declarative
set_is_editing(True)
set_new_first_name(user.first_name)
```

### 5. 把 UI 抽取成元件

- 每個「功能區塊」做成一個 `@ft.component`
- 元件內使用 `use_state` 來管理在地 UI 狀態
- 元件外共享的狀態全部放在 observable dataclass

---

## 五、Mindset Shift（心態轉變）

**核心原則**：determinism（確定性）— 給定相同狀態，元件應返回相同 UI。

兩個階段：
1. **狀態變了**（操作 observable）
2. **Flet 自動重新渲染**（依據新狀態）

**不是**：手動開關控制項、手動呼叫 update。

---

## 六、啟動方式的差異

| 寫法 | 啟動方式 |
|---|---|
| Imperative | `ft.run(main)`，`main(page: ft.Page)` 接收 page |
| Declarative | `ft.run(lambda page: page.render(AppView))` |

`page.render()` 是 0.82.x 的新 API，用於宣告式渲染。

---

## 七、與 0.28.3 的關係

**重要**：這個 Declarative 寫法是 **0.82.x 全新引進的**。
- 0.28.3 **沒有** `@ft.observable`、`@ft.component`、`ft.use_state`、`page.render()`
- 0.28.3 只能用 **Imperative** 方式（`page.update()`）
- 這個 CRUD 範例是 **0.82.x 宣傳的核心賣點**

---

## 八、API Reference 結構（https://docs.flet.dev/api-reference/）

| 類別 | 路徑 | 說明 |
|---|---|---|
| Controls | `/controls/` | UI 構建基塊，含屬性/事件/範例 |
| Services | `/services/` | 設備和平臺能力（感測器/儲存/權限） |
| CLI | `/cli/` | flet 命令（建立/執行/封裝/除錯） |
| Types | `/types/` | 核心類型、枚舉、事件、異常 |
| Binary Packages | `/reference/binary-packages-android-ios/` | Android/iOS 預編套件 |
| Environment Variables | `/reference/environment-variables/` | 執行期設定開關 |

---

## 九、文件 URL 對照

| 主題 | URL |
|---|---|
| 首頁 | https://docs.flet.dev/ |
| 總索引 | https://docs.flet.dev/docs |
| Declarative CRUD | https://docs.flet.dev/cookbook/declarative-vs-imperative-crud-app/ |
| Controls 總覽 | https://docs.flet.dev/controls/ |
| Page | https://docs.flet.dev/controls/page/ |
| Navigation | https://docs.flet.dev/cookbook/navigation-and-routing/ |
| Logging | https://docs.flet.dev/cookbook/logging/ |
| Drag and Drop | https://docs.flet.dev/cookbook/drag-and-drop/ |
| Publishing | https://docs.flet.dev/publish/ |
