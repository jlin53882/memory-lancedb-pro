# Flet 0.82.2 輸入控制項 — 學習筆記

> 來源：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\`
> 版本：0.82.2 | 日期：2026-03-23

---

## TextField（重要：prefix_text 狀態）

### prefix_text 狀態
**`prefix_text` 在 0.82.2 中不存在。**  
搜尋整個 `TextField` 類別，沒有任何 `prefix_text` 或 `suffix_text` 屬性。

如果需要 prefix/suffix 效果，目前只能透過 `prefix` / `suffix`（接受 `Control`物件）來實現，這屬於 `FormFieldControl` 的基底屬性。

### 事件：on_change vs on_submit

| 事件 | 觸發時機 |
|------|----------|
| `on_change` | 使用者**輸入改變**時觸發（每打一字觸發一次） |
| `on_submit` | 使用者按下 **Enter** 鍵時觸發（需 field 取得 focus） |

```python
# on_change：即時監聽輸入
ft.TextField(
    label="搜尋",
    on_change=lambda e: print(f"目前輸入：{e.control.value}")
)

# on_submit：按 Enter 後才處理
ft.TextField(
    label="名稱",
    on_submit=lambda e: print(f"提交：{e.control.value}")
)
```

### read_only 行為
- `read_only=True`：文字**不可編輯**，但仍然**可以選取（selectable）**
- 不同於 `disabled`，`disabled=True` 通常連選取都無法操作
- `on_change` 在 `read_only=True` 時**不會觸發**（因為值無法變動）

### 其他重要屬性
- `value: str` — 目前文字內容
- `selection: Optional[TextSelection]` — 目前選取範圍/游標位置
- `max_length` — 最大字數（預設無限制）
- `password: bool` — 遮蔽輸入（預設 False）
- `multiline: bool` — 多行模式（預設 False）
- `shift_enter: bool` — True 時，多行模式下 Enter 提交、Shift+Enter 新增一行

---

## Dropdown（重要：on_select 取代 on_change）

### on_select 取代 on_change
**`Dropdown` 沒有 `on_change`**，使用 `on_select` 作為選項變更事件。

```python
def dropdown_changed(e: ft.ControlEvent):
    print(f"選擇了：{e.control.value}")  # e.control.value 是 Dropdown 本身

dropdown = ft.Dropdown(
    value="alice",
    options=[
        ft.DropdownOption(key="alice", text="Alice"),
        ft.DropdownOption(key="bob", text="Bob"),
    ],
    on_select=dropdown_changed,
)
```

### value 取值方式
- `dropdown.value` → 取得**目前選項的 key**（字串），非 text
- `dropdown.text` → 取得文字輸入框中的**目前文字**（可用於可編輯 dropdown）

```python
# 取 key（最常用）
selected_key = dropdown.value  # 例如 "alice"

# 迴圈找對應 text
selected_text = next(
    (opt.text for opt in dropdown.options if opt.key == dropdown.value),
    None
)
```

### DropdownOption 結構
```python
ft.DropdownOption(
    key="alice",          # 選項的唯一識別碼（會成為 value）
    text="Alice",         # 顯示文字
    content=None,         # 自訂 Control（設定後 text/key 被忽略）
    leading_icon=None,     # 選項前的圖示
    trailing_icon=None,   # 選項後的圖示
)
```

### 其他重要屬性
- `enable_filter: bool` — 啟用輸入過濾功能（預設 False）
- `editable: bool` — 允許使用者自行輸入（預設 False）
- `on_text_change` — 當輸入文字改變時觸發（與 `on_select` 不同）
- `expanded_insets` — 展開式下拉選單的內距

---

## Slider（on_change vs on_change_end）

### 三種事件完整解析

| 事件 | 觸發時機 |
|------|----------|
| `on_change_start` | 使用者**開始拖動**時（放開 thumb 前就觸發） |
| `on_change` | 拖動過程中**值變動**時（拖到哪觸發到哪，頻率高） |
| `on_change_end` | 使用者**放開 thumb**、結束拖動時 |

```python
def on_start(e):
    print("開始拖動")

def on_change(e):
    print(f"目前值：{e.control.value}")  # 拖動中持續更新

def on_end(e):
    print(f"最終值：{e.control.value}")  # 放開後取得最終值

ft.Slider(
    min=0, max=100, value=50,
    on_change_start=on_start,
    on_change=on_change,
    on_change_end=on_end,
)
```

### 重要屬性
- `value: Optional[Number]` — 目前值（None 時使用 min）
- `label: Optional[str]` — 顯示標籤（可用 `{value}` 動態替換，如 `"音量：{value}"`）
- `divisions: Optional[int]` — 離散分段數（搭配 label 使用）
- `secondary_track_value` — 緩衝進度條（如影片播放與緩衝對比）
- `interaction: SliderInteraction` — 限制互動方式（TAP_AND_SLIDE / TAP_ONLY / SLIDE_ONLY / SLIDE_THUMB）

---

## DatePicker（正確用法）

### Constructor 參數

```python
ft.DatePicker(
    value=datetime(2024, 1, 1),        # 初始選中日期（預設今日）
    modal=False,                        # 是否強制關閉才能點別處（預設 False）
    first_date=datetime(1900, 1, 1),   # 可選最早期限
    last_date=datetime(2050, 12, 31),  # 可選最晚期限
    current_date=datetime.now(),       # 今日標示
    entry_mode=DatePickerEntryMode.CALENDAR,  # 初始模式
    help_text="選擇日期",
    cancel_text="取消",
    confirm_text="確認",
    on_change=handle_change,
)
```

### 重要屬性
- `value: Optional[DateTimeValue]` — 目前選中的日期（按確認後更新）
- `entry_mode: DatePickerEntryMode` — 初始輸入模式
  - `CALENDAR` — 日曆選擇
  - `INPUT` — 文字輸入
  - `CALENDAR_ONLY` — 只能日曆選
  - `INPUT_ONLY` — 只能文字輸入
- `on_change` — **按確認按鈕後**才觸發，`e.data` 包含選中的日期

### 開啟方式：`open()`（不是 pick_date()）
**`DatePicker` 沒有 `pick_date()` 方法。** 正確做法：

```python
date_picker = ft.DatePicker(on_change=handle_date_change)

def handle_date_change(e: ft.ControlEvent):
    print(f"選擇的日期：{e.data}")  # 或直接取 date_picker.value

# 將 date_picker 加入 page 後，用 open() 開啟
async def open_picker(e):
    date_picker.open()
    await e.page.update()

# 或者直接用 page.show_dialog()（兩者皆可）
async def open_picker_v2(e):
    e.page.show_dialog(date_picker)
```

### on_change 行為
- **按確認（OK）按鈕後** `value` 才會更新，`on_change` 才會觸發
- **按取消**不會觸發 `on_change`，`value` 維持原值
- 沒有 `on_cancel` 事件（需自行處理 UI 邏輯）

---

## FilePicker（重要：on_result 不在 constructor）

### ⚠️ on_result 不存在！
**Flet 0.82.2 的 `FilePicker` 沒有 `on_result` 屬性。**  
只有一個事件：`on_upload`（上傳進度回呼）。

正確用法是 **`pick_files()` 作為 async 方法直接返回結果**，不靠事件回調。

```python
file_picker = ft.FilePicker()  # constructor 無 callback 參數

# 錯誤示範（0.82.2 不支援）
# file_picker = ft.FilePicker(on_result=callback)  # AttributeError!

# 正確做法：async/await 取得結果
async def pick(e):
    files = await file_picker.pick_files(
        dialog_title="選擇檔案",
        file_type=ft.FilePickerFileType.IMAGE,
        allow_multiple=True,
        with_data=False,  # True 時可取檔案內容（記憶體）
    )
    for f in files:
        print(f"檔名：{f.name}, 路徑：{f.path}, 大小：{f.size}")

ft.ElevatedButton("選檔案", on_click=pick)
```

### pick_files() 方法結構

```python
async def pick_files(
    self,
    dialog_title: Optional[str] = None,       # 對話框標題
    initial_directory: Optional[str] = None,   # 初始目錄
    file_type: FilePickerFileType = FilePickerFileType.ANY,  # 檔案類型
    allowed_extensions: Optional[list[str]] = None,  # 自訂副檔名（如 ["pdf", "doc"]）
    allow_multiple: bool = False,             # 允许多选
    with_data: bool = False,                   # 是否讀取檔案內容（bytes）
) -> list[FilePickerFile]:
```

### FilePickerFile 結構

```python
@dataclass
class FilePickerFile:
    id: int           # Flet 分配的檔案 ID（上傳時優先用）
    name: str         # 檔案名稱（不含路徑）
    size: int         # 檔案大小（bytes）
    path: Optional[str]  # 檔案完整路徑（Web 模式永遠是 None）
    bytes: Optional[bytes]  # 檔案內容（需 with_data=True 才會填入）
```

### 其他方法

| 方法 | 用途 |
|------|------|
| `upload(files: list[FilePickerUploadFile])` | 上傳已選取的檔案（需先 `pick_files()`） |
| `get_directory_path()` | 開啟資料夾選擇對話框（回傳路徑，Web 不支援） |
| `save_file()` | 開啟儲存檔案對話框（Mobile/Web 需提供 `src_bytes`） |

```python
# 上傳用法
files = await file_picker.pick_files(allow_multiple=True)
upload_descriptors = [
    ft.FilePickerUploadFile(
        upload_url=page.get_upload_url(f.name),
        id=f.id,
    )
    for f in files
]
await file_picker.upload(upload_descriptors)
```

### FilePicker 是 Service，行為不同
- `FilePicker` 繼承自 `Service`，不是 `Control`
- 不需要也不支援 `on_result`（這是早期版本的設計）
- `on_upload` 是唯一的事件回調（用於上傳進度）

---

## 常用程式碼範例

### TextField 即時搜尋（結合 on_change）
```python
def search(e: ft.ControlEvent):
    query = e.control.value
    results = [item for item in all_items if query.lower() in item.lower()]
    list_view.controls = [ft.Text(i) for i in results]
    page.update()

ft.TextField(
    label="搜尋",
    on_change=search,
    autofocus=True,
)
```

### Dropdown 連動 TextField
```python
user_map = {"alice": "Alice Smith", "bob": "Bob Jones"}

def on_chosen(e: ft.ControlEvent):
    full_name.value = user_map.get(dropdown.value, "")
    full_name.update()

dropdown = ft.Dropdown(options=[...], on_select=on_chosen)
full_name = ft.Text()
```

### Slider 即時預覽
```python
def on_value_changed(e: ft.ControlEvent):
    label.value = f"目前進度：{e.control.value:.0f}%"
    label.update()

slider = ft.Slider(min=0, max=100, value=50, on_change=on_value_changed)
label = ft.Text("目前進度：50%")
```

### DatePicker + FilePicker 組合
```python
date_picker = ft.DatePicker()
file_picker = ft.FilePicker()
page.overlay.extend([date_picker, file_picker])  # 重要：需加入 overlay

async def show_date(e):
    date_picker.open()
    await page.update()

async def show_files(e):
    files = await file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
    print([f.name for f in files])
```

---

## 重要發現與注意事項

### 1. FilePicker 的 on_result 是舊 API
很多網路範例寫的是 `FilePicker(on_result=callback)`，但 **Flet 0.82.2 已移除此用法**。現在只能靠 `await file_picker.pick_files()` 取得結果。實作者需要是 `async` 函式。

### 2. DatePicker 的開啟方式是 open() 或 show_dialog()
不是 `pick_date()`，也沒有該方法。需配合 `page.overlay` 或 `page.show_dialog()` 使用。

### 3. TextField 的 prefix_text 在此版本不存在
如果看到舊程式碼使用 `prefix_text="NT$"`，那是早期版本或不同 Widget 框架。Flet 0.82.2 若需要 prefix，要用 `FormFieldControl` 的 `prefix` 屬性（接受 Control）。

### 4. Dropdown 的值是 key 而非 text
`dropdown.value` 取得的是 `DropdownOption.key`，要顯示文字需另外查詢 `opt.text`。

### 5. Slider 的 on_change 頻率很高
`on_change` 在拖動過程中**每像素移動都會觸發**，如果要做 expensive 運算（如網路請求），應使用 `on_change_end` 取代。

### 6. DatePicker on_change 只在確認後觸發
按 Cancel 或點 dialog 外面關閉都不會觸發 `on_change`。需要自己維護狀態或用 `on_dismiss` 處理取消邏輯。
