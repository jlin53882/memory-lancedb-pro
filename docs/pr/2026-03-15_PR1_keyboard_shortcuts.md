# PR #1：鍵盤快捷鍵系統

## 1. 概述

在 Flet 應用中新增全域鍵盤快捷鍵系統，讓使用者可以用鍵盤快速操作，提升效率。

## 2. 設計目標

- 全域快捷鍵：⌘1-9 快速跳轉頁面、⌘F 搜尋、⌘S 儲存
- 符合專業軟體操作習慣
- 不影響現有功能

## 3. 實作方式

### 3.1 建立快捷鍵模組

建立 `app/ui/keyboard_shortcuts.py`：

```python
"""鍵盤快捷鍵模組"""

import flet as ft

# 快捷鍵定義
SHORTCUTS = {
    # 全域導航
    "1": ("設定", "view_0"),
    "2": ("規則", "view_1"),
    "3": ("快取", "view_2"),
    # ...
    
    # 功能鍵
    "f": ("搜尋", "focus_search"),
    "s": ("儲存", "save"),
    "r": ("重新整理", "reload"),
    ",": ("設定", "open_settings"),
}

def handle_keyboard_event(e: ft.KeyboardEvent, page: ft.Page) -> bool:
    """處理鍵盤事件"""
    key = e.key.lower()
    ctrl = e.ctrl or e.meta
    
    if ctrl and key in SHORTCUTS:
        # 執行對應動作
        return True
    return False
```

### 3.2 在 main.py 註冊事件

在 page 建立後註冊鍵盤事件處理器。

### 3.3 視覺提示

在頁面底部顯示快捷鍵提示列（可隱藏）。

## 4. 驗收標準

- [ ] ⌘1-9 可跳轉到對應頁面
- [ ] ⌘F 可聚焦搜尋框
- [ ] ⌘S 可儲存當前設定
- [ ] ⌘R 可重新整理
- [ ] Esc 可關閉彈出視窗

## 5. 風險

- 快捷鍵與瀏覽器快捷鍵衝突 → 使用 ⌘ (Command) 而非 Ctrl
