# PR #5：統一狀態元件

## 1. 概述

建立統一的 Loading / Empty / Error 狀態顯示元件，確保各頁面視覺一致。

## 2. 設計目標

- 統一的載入中狀態
- 統一的空資料狀態
- 統一的錯誤狀態
- 可自定義圖標、標題、訊息、操作按鈕

## 3. 實作方式

### 3.1 建立狀態元件

在 `app/ui/components.py` 中新增：

```python
def loading_state(
    message: str = "載入中...",
    show_spinner: bool = True,
) -> ft.Container:
    """統一的載入狀態顯示"""

def empty_state(
    icon: str,
    title: str,
    message: str,
    action_button: ft.Control | None = None,
) -> ft.Container:
    """統一的空狀態顯示"""

def error_state(
    icon: str,
    title: str,
    message: str,
    retry_button: ft.Control | None = None,
) -> ft.Container:
    """統一的錯誤狀態顯示"""
```

### 3.2 整合到各頁面

替換現有的自定義狀態顯示。

## 4. 驗收標準

- [ ] 各頁面使用統一的 Loading 狀態
- [ ] 各頁面使用統一的 Empty 狀態
- [ ] 各頁面使用統一的 Error 狀態
- [ ] 支援自定義圖標和訊息

## 5. 風險

- 現有程式碼修改 → 只影響顯示外觀，不影響功能
