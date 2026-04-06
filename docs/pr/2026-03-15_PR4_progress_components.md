# PR #4：進度條統一元件

## 1. 概述

建立統一的進度條元件，用於長時間操作的視覺反饋。

## 2. 設計目標

- 顯示進度百分比
- 顯示 ETA（預估剩餘時間）
- 支援取消操作
- 統一外觀

## 3. 實作方式

### 3.1 建立 ProgressCard 元件

在 `app/ui/components.py` 中新增：

```python
class ProgressCard(ft.Container):
    """進度條卡片元件"""
    
    def __init__(
        self,
        title: str,
        current: int,
        total: int,
        on_cancel=None,
    ):
        # 進度條
        # 百分比顯示
        # ETA 計算
        # 取消按鈕
```

### 3.2 整合到長時間操作頁面

- CacheView：rebuild index、reload 等
- TranslationView：翻譯過程

### 3.3 ETA 計算

```python
def calculate_eta(elapsed_time, current, total):
    if current == 0:
        return None
    rate = current / elapsed_time
    remaining = total - current
    return remaining / rate
```

## 4. 驗收標準

- [ ] 長時間操作顯示進度條
- [ ] 顯示百分比
- [ ] 顯示 ETA
- [ ] 支援取消操作
- [ ] 統一外觀

## 5. 風險

- ETA 不準確 → 初期使用 indeterminate 模式
