# PR #3：卡片收合功能 + 統一樣式

## 1. 概述

擴展現有的 `styled_card` 元件，增加收合功能和更豐富的視覺樣式。

## 2. 設計目標

- 每個卡片可收合/展開
- 統一所有頁面的區塊視覺樣式
- 支援「閃電」快捷操作

## 3. 實作方式

### 3.1 擴展 styled_card

更新 `app/ui/components.py` 中的 `styled_card` 函數：

```python
def styled_card(
    *,
    title: str,
    icon: str,
    content: ft.Control,
    expand: bool = False,
    icon_color: str = ft.Colors.BLUE_GREY_700,
    collapsible: bool = False,  # 新增
    default_collapsed: bool = False,  # 新增
    quick_actions: list = None,  # 新增
) -> ft.Container:
    """統一的「區塊卡片」外觀（支援收合）"""
```

### 3.2 收合動畫

使用 Flet 的動畫 API 實現平滑收合效果。

### 3.3 快速操作按鈕

右上角增加「閃電」圖標，點擊顯示常用操作選單。

## 4. 驗收標準

- [ ] 卡片支援收合/展開
- [ ] 收合狀態會保存到設定
- [ ] 統一各頁面的卡片樣式
- [ ] 支援快速操作選單

## 5. 風險

- 收合狀態保存 → 存到 config.json
