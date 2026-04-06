# MergeView UI 收斂設計原則｜2026-03-19 實戰記錄

> 這是今天實際修改 merge_view.py 的經驗整理，不是理論，是踩過坑後收斂出來的實戰原則。

---

## 核心心法

| 心法 | 說明 |
|------|------|
| 先求可用，不追求無限美化 | 停損點：結構成形、操作合理、閱讀負擔低 |
| 設定頁不是文件頁 | 每個設定只講一句，不寫成規格文件 |
| 控件要跟標題形成同一組 | 不要讓說明文字和控件擠在同一行 |
| scroll 是保底，不是掩蓋壞排版的工具 | 先把佈局做好，scroll 是最後防線 |
| **UI 改動後必做驗證** | py_compile → import → pytest → uv run main.py（順序不能跳） |

---

## Flet 實戰要點（0.28.3）

### ListView 常見錯誤
```
❌ ft.ListView(scroll="auto", direction=ft.Axis.HORIZONTAL)
✅ ft.ListView(horizontal=True, auto_scroll=True)
```
Flet 0.28.3 ListView：無 `scroll=` 參數，無 `direction=` 參數。

### Patchouli 設定區結構
外層灰底 Container + 內層 ft.Column（spacing=6 適中）：
```python
ft.Container(
    bgcolor=ft.Colors.GREY_100,
    border_radius=8,
    padding=10,
    content=ft.Column([
        ft.Text("Patchouli 進階設定", size=12, weight=W_600),
        ft.Container(height=8),
        ft.Row([self.switch], spacing=15),  # switch 同一行
        ft.Text("說明", size=11, color=GREY_600),  # 說明下一行
        self._skip_disabled_note(),  # disabled note 綁在對應設定下方
        ft.Container(height=10),
        # ... 下一列
    ], spacing=6),
)
```

### Threshold 數值欄位
讓輸入框視覺收縮，不要長長一條：
```python
ft.Row(
    [
        ft.Text("en_us 跳過門檻：", size=11, color=GREY_600),
        ft.Container(content=self.patchouli_threshold_field, width=80),
        ft.Text("範圍：0.0-1.0", size=10, color=GREY_400),
    ],
    alignment=ft.MainAxisAlignment.START,
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
)
```

---

## 驗證 SOP（每次必做）

```bash
# 1. 編譯
python -m py_compile app/views/merge_view.py

# 2. Import
.venv/Scripts/python.exe -c "from app.views.merge_view import MergeView; print('ok')"

# 3. 測試
.venv/Scripts/python.exe -m pytest tests/ -q --tb=short

# 4. UI
uv run main.py
```

**順序不能跳**，跳過測試會浪費更多來回時間。

---

## 適用情境

- 設定頁有 2-3 個開關 + 1 個 threshold
- 不需要高階美化，只需要「可讀、可操作」
- 遇到 UI 修改需求：先問「是否已達停損點？」
