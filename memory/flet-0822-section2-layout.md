# Flet 0.82.2 Layout 控制項參考

> version: flet:0.82.2
> 整理日期：2026-03-22
> 資料來源：docs.flet.dev（官方文件）

---

## 概述

Layout 控制項主要分為「容器佈局」與「簡單分隔」兩大類：

| 控制項 | 類型 | 說明 |
|--------|------|------|
| `Row` | 核心佈局 | 水平線性排列 |
| `Column` | 核心佈局 | 垂直線性排列 |
| `Stack` | 核心佈局 | 絕對定位疊加（LIFO） |
| `Container` | 核心佈局 | 單一子元素的裝飾與定位 |
| `ResponsiveRow` | 核心佈局 | 響應式虛擬格線（12欄） |
| `ListTile` | 簡單佈局 | 單列列表項目 |
| `Divider` | 分隔線 | 水平分隔 |
| `GridView` | 核心佈局 | 二維格線排列 |

---

## 1. Row

**文件**：[https://docs.flet.dev/controls/row/](https://docs.flet.dev/controls/row/)

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `alignment` | `MainAxisAlignment` | 主軸（水平）對齊：START / CENTER / END / SPACE_BETWEEN / SPACE_AROUND / SPACE_EVENLY |
| `vertical_alignment` | `CrossAxisAlignment` | 交叉軸（垂直）對齊：START / CENTER / END / BASELINE / STRECH |
| `controls` | `list[Control]` | 子控制項列表 |
| `spacing` | `Number` | 子控制項之間的間距（像素） |
| `wrap` | `bool` | 是否換行（預設 False） |
| `run_spacing` | `Number` | 換行後「行」之間的間距 |
| `run_alignment` | `MainAxisAlignment` | 換行時，每一行在交叉軸上的對齊 |
| `tight` | `bool` | 為 True 時佔滿可用水平空間；為 False 時只佔子項所需空間 |
| `intrinsic_height` | `bool` | 為 True 時，Row 高度等於最高子項的高度（預設 False） |

**繼承**：`LayoutControl`, `ScrollableControl`, `AdaptiveControl`

### 嵌套規則
- ✅ Row → 可嵌套：任何 Control（含另一個 Row/Column/Stack）
- ✅ 被嵌套時：常用 `expand` 屬性讓子項填滿剩餘空間

### 與 0.28.3 差異

| 屬性/功能 | 0.82.2 | 0.28.3 | 備註 |
|-----------|--------|--------|------|
| `tight` | ✅ 有 | ❌ 無 | 0.82.2 新增 |
| `intrinsic_height` | ✅ 有 | ❌ 無 | 0.82.2 新增 |
| `wrap` | ✅ 有 | ✅ 有 | 0.28.3 也有，但行為可能不同 |
| `run_spacing` / `run_alignment` | ✅ 有 | ❌ 待驗證 | 0.28.3 可能沒有換行相關屬性 |

---

## 2. Column

**文件**：[https://docs.flet.dev/controls/column/](https://docs.flet.dev/controls/column/)

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `alignment` | `MainAxisAlignment` | 主軸（垂直）對齊 |
| `horizontal_alignment` | `CrossAxisAlignment` | 交叉軸（水平）對齊 |
| `controls` | `list[Control]` | 子控制項列表 |
| `spacing` | `Number` | 子控制項之間的間距 |
| `wrap` | `bool` | 是否換列（預設 False） |
| `run_spacing` | `Number` | 換列後「列」之間的間距 |
| `run_alignment` | `MainAxisAlignment` | 換列時，每一列在交叉軸上的對齊 |
| `tight` | `bool` | 為 True 時佔滿可用垂直空間 |
| `intrinsic_width` | `bool` | 為 True 時，Column 寬度等於最寬子項的寬度（預設 False） |

**繼承**：`LayoutControl`, `ScrollableControl`, `AdaptiveControl`

### 嵌套規則
- ✅ Column → 可嵌套：任何 Control（含另一個 Column/Row/Stack）
- ✅ 被嵌套時：常用 `expand` 屬性讓子項填滿剩餘空間

### 與 0.28.3 差異

| 屬性/功能 | 0.82.2 | 0.28.3 | 備註 |
|-----------|--------|--------|------|
| `tight` | ✅ 有 | ❌ 無 | 0.82.2 新增 |
| `intrinsic_width` | ✅ 有 | ❌ 無 | 0.82.2 新增 |
| `wrap` | ✅ 有 | ✅ 有 | 0.28.3 也有 |
| `run_spacing` / `run_alignment` | ✅ 有 | ❌ 待驗證 | 0.28.3 可能沒有 |

---

## 3. Stack

**文件**：[https://docs.flet.dev/controls/stack/](https://docs.flet.dev/controls/stack/)

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `alignment` | `Alignment` | 非定位子元素的對齊（使用 `ft.Alignment`） |
| `clip_behavior` | `ClipBehavior` | 內容超出時的裁剪行為 |
| `controls` | `list[Control]` | 子控制項列表（最後的在最上層，LIFO） |
| `fit` | `StackFit` | 非定位子項如何調整尺寸：FILL / EXPAND / PASSTHROUGH |

**繼承**：`LayoutControl`, `AdaptiveControl`

### 嵌套規則
- ✅ Stack → 可嵌套：任何 Control（含 Row/Column/Container）
- 子項可用 `left`, `top`, `right`, `bottom` 絕對定位（繼承自 `LayoutControl`）
- 定位屬性：需查 `LayoutControl` 文件（`top`, `bottom`, `left`, `right`）

### 與 0.28.3 差異

| 屬性/功能 | 0.82.2 | 0.28.3 | 備註 |
|-----------|--------|--------|------|
| `fit` | ✅ 有 | ❌ 待驗證 | 0.28.3 可能有但值不同 |
| `clip_behavior` | ✅ 有 | ❌ 待驗證 | 0.28.3 可能有 |
| `alignment`（Stack 專用） | ✅ 有 | ✅ 有 | 0.28.3 也有，行為相似 |

---

## 4. Container

**文件**：[https://docs.flet.dev/controls/container/](https://docs.flet.dev/controls/container/)

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `alignment` | `Alignment \| None` | 內容在容器內的對齊 |
| `bgcolor` | `ColorValue \| None` | 背景顏色 |
| `border` | `Border \| None` | 邊框 |
| `border_radius` | `BorderRadiusValue \| None` | 邊框圓角 |
| `padding` | `PaddingValue \| None` | 內距（內容與邊界之間） |
| `content` | `Control \| None` | 單一子控制項 |
| `clip_behavior` | `ClipBehavior \| None` | 內容裁剪行為 |
| `gradient` | `Gradient \| None` | 漸層背景 |
| `image` | `DecorationImage \| None` | 背景圖片 |
| `shadow` | `BoxShadowValue \| None` | 陰影 |
| `shape` | `BoxShape` | 形狀：RECTANGLE / CIRCLE |
| `url` | `str \| Url \| None` | 點擊時開啟 URL |
| `ink` | `bool` | 是否顯示墨水波紋效果（點擊反饋） |
| `ink_color` | `ColorValue \| None` | 墨水波紋的顏色 |
| `animate` | `AnimationValue \| None` | 隱式動畫（漸變屬性值） |
| `blur` | `BlurValue \| None` | 高斯模糊效果 |
| `blend_mode` | `BlendMode \| None` | 混合模式 |
| `color_filter` | `ColorFilter \| None` | 顏色濾鏡 |
| `foreground_decoration` | `BoxDecoration \| None` | 前景裝飾 |
| `dark_theme` | `Theme \| None` | 深色模式下的嵌套主題 |
| `theme` | `Theme \| None` | 嵌套主題 |
| `theme_mode` | `ThemeMode \| None` | 主題模式覆寫 |
| `ignore_interactions` | `bool` | 忽略所有互動事件 |

**事件**：`on_click`, `on_hover`, `on_long_press`, `on_tap_down`

**繼承**：`LayoutControl`, `AdaptiveControl`

### 嵌套規則
- ⚠️ **重要**：Container 只能容納**單一**子控制項（`content`）
- ✅ 可嵌套：任何 Control
- 若要放多個子項，必須先用 Row/Column/Stack 包裝

### 與 0.28.3 差異

| 屬性/功能 | 0.82.2 | 0.28.3 | 備註 |
|-----------|--------|--------|------|
| `ink` / `ink_color` | ✅ 有 | ❌ 無 | 0.82.2 新增（Material Ink 效果） |
| `animate` | ✅ 有 | ❌ 待驗證 | 隱式動畫，0.28.3 可能沒有 |
| `blur` | ✅ 有 | ❌ 無 | 高斯模糊，0.28.3 沒有 |
| `blend_mode` | ✅ 有 | ❌ 無 | 混合模式，0.28.3 沒有 |
| `color_filter` | ✅ 有 | ❌ 無 | 顏色濾鏡，0.28.3 沒有 |
| `image` | ✅ 有 | ❌ 待驗證 | 背景圖片，0.28.3 可能沒有 |
| `foreground_decoration` | ✅ 有 | ❌ 無 | 前景裝飾，0.28.3 沒有 |
| `ignore_interactions` | ✅ 有 | ❌ 無 | 忽略互動，0.28.3 沒有 |
| `dark_theme` | ✅ 有 | ❌ 無 | 嵌套深色主題，0.28.3 沒有 |
| `theme_mode` | ✅ 有 | ❌ 無 | 主題模式覆寫，0.28.3 沒有 |

---

## 5. ResponsiveRow

**文件**：[https://docs.flet.dev/controls/responsiverow/](https://docs.flet.dev/controls/responsiverow/)

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `alignment` | `MainAxisAlignment` | 主軸對齊 |
| `vertical_alignment` | `CrossAxisAlignment` | 交叉軸對齊 |
| `controls` | `list[Control]` | 子控制項列表 |
| `columns` | `ResponsiveNumber` | 虛擬欄數（預設 12） |
| `spacing` | `ResponsiveNumber` | 欄間距（可響應式） |
| `run_spacing` | `ResponsiveNumber` | 行間距（可響應式） |
| `breakpoints` | `dict[ResponsiveRowBreakpoint \| str, Number]` | 自定義斷點（如 `{"phone": 0, "tablet": 540}`） |

### 嵌套規則
- ✅ ResponsiveRow → 可嵌套：任何 Control
- 子項需使用 `col` 屬性（繼承自 `Control`）指定佔欄數

### 斷點（`ResponsiveRowBreakpoint`）
- `XS`：超小（行動電話）
- `SM`：小（小平板）
- `MD`：中（平板）
- `LG`：大（桌面）
- `XL`：超大

### 使用範例
```python
ft.ResponsiveRow(
    col={
        ft.ResponsiveRowBreakpoint.XS: 12,  # 手機：佔滿12欄
        ft.ResponsiveRowBreakpoint.MD: 6,   # 平板：佔一半
        ft.ResponsiveRowBreakpoint.LG: 3,   # 桌面：佔1/4
    }
)
```

### 與 0.28.3 差異

| 屬性/功能 | 0.82.2 | 0.28.3 | 備註 |
|-----------|--------|--------|------|
| ResponsiveRow 整體 | ✅ 有 | ❌ 無 | 0.28.3 沒有此控制項 |

---

## 6. 其他 Layout 相關控制項

### 6.1 Divider

**文件**：[https://docs.flet.dev/controls/divider/](https://docs.flet.dev/controls/divider/)

水平分隔線。屬於簡單裝飾控制項，不算嚴格意義的「容器」。

### 6.2 ListTile

**文件**：[https://docs.flet.dev/controls/listtile/](https://docs.flet.dev/controls/listtile/)

單列列表項目，包含 title、leading、trailing 等配置。

### 6.3 GridView

二維格線排列。適用於大量項目的網格式排列。

---

## Layout 與 0.28.3 差異對照

> ⚠️ **重要前提**：根據先前分析（`flet_docs_vs_source_v0.28.3.md`），文件（0.82.2 API）與原始碼（0.28.3）有**重大差異**，不得直接套用文件 API，必須以原始碼為準。

### 綜合差異表

| 功能 | 0.82.2 文件 | 0.28.3 原始碼 | 風險 |
|------|------------|--------------|------|
| `Row.tight` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Row.intrinsic_height` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Column.tight` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Column.intrinsic_width` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Row.run_spacing` | ✅ | ❌ 可能沒有 | 高 |
| `Column.run_spacing` | ✅ | ❌ 可能沒有 | 高 |
| `Container.ink` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.animate` | ✅ | ❌ 可能沒有 | 高 |
| `Container.blur` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.blend_mode` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.color_filter` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.foreground_decoration` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.dark_theme` | ✅ | ❌ 沒有 | 高：新屬性 |
| `Container.ignore_interactions` | ✅ | ❌ 沒有 | 高：新屬性 |
| `ResponsiveRow` | ✅ | ❌ 沒有 | 高：整個控制項不存在 |
| `Stack.fit` | ✅ | ❌ 待驗證 | 中 |
| `Stack.clip_behavior` | ✅ | ❌ 待驗證 | 中 |
| `GridView` | ✅ | ✅ 有 | 低：兩版都有 |
| `Divider` | ✅ | ✅ 有 | 低：兩版都有 |
| `ListTile` | ✅ | ✅ 有 | 低：兩版都有 |

### 遷移建議

1. **千萬不要**在 0.28.3 專案中使用 `ResponsiveRow`
2. **千萬不要**在 0.28.3 專案中使用 `Container.ink`、`Container.blur`、`Container.blend_mode`
3. `Row.tight` / `Column.tight` / `Row.intrinsic_height` / `Column.intrinsic_width` 在 0.28.3 不存在
4. 舊版佈局替換方案：
   - `tight=True` → 依靠 `expand` + 父容器寬度控制
   - `intrinsic_height=True` → 手動設定固定高度或依靠內容撐開

---

## ✅ 已驗證 vs ❌ 待驗證 清單

### ✅ 已驗證（文件有，0.28.3 大致確認）

| 項目 | 說明 |
|------|------|
| Row `alignment` / `vertical_alignment` / `spacing` / `wrap` | 0.28.3 有，功能相同 |
| Column `alignment` / `horizontal_alignment` / `spacing` / `wrap` | 0.28.3 有，功能相同 |
| Stack `alignment` | 0.28.3 有，行為相似 |
| Container `alignment` / `padding` / `margin` / `bgcolor` / `border` / `border_radius` | 0.28.3 有 |
| GridView | 0.28.3 有 |
| Divider | 0.28.3 有 |
| ListTile | 0.28.3 有 |

### ❌ 待驗證（文件有，0.28.3 未確認）

| 項目 | 說明 |
|------|------|
| Row `tight` | 0.28.3 文件沒有提及，需要查原始碼確認 |
| Row `intrinsic_height` | 0.28.3 沒有，需要查原始碼確認 |
| Row `run_spacing` / `run_alignment` | 換行相關屬性，0.28.3 可能沒有 |
| Column `tight` | 需要查原始碼確認 |
| Column `intrinsic_width` | 0.28.3 沒有 |
| Column `run_spacing` / `run_alignment` | 需要查原始碼確認 |
| Stack `fit` | 需要查原始碼確認 |
| Stack `clip_behavior` | 需要查原始碼確認 |
| Container `ink` / `ink_color` | 0.28.3 沒有（Material Ink 是新屬性） |
| Container `animate` | 需要查原始碼確認 |
| Container `blur` | 0.28.3 沒有 |
| Container `blend_mode` | 0.28.3 沒有 |
| Container `color_filter` | 0.28.3 沒有 |
| Container `image` | 需要查原始碼確認 |
| Container `foreground_decoration` | 0.28.3 沒有 |
| Container `dark_theme` / `theme` / `theme_mode` | 0.28.3 可能沒有嵌套主題 |
| Container `ignore_interactions` | 0.28.3 沒有 |
| ResponsiveRow | 整個控制項在 0.28.3 不存在 |

---

## 嵌套規則速查

```
Page
 └─ LayoutControl（所有以下都繼承）
     ├─ Row
     │    └─ [Control, Row, Column, Stack, Container, ...]
     │         └─ 若要多個子項：直接放
     │         └─ 若要填滿空間：子項設 expand=True
     │
     ├─ Column
     │    └─ [Control, Row, Column, Stack, Container, ...]
     │         └─ 若要多個子項：直接放
     │         └─ 若要填滿空間：子項設 expand=True
     │
     ├─ Stack
     │    └─ [Control, Row, Column, Container, ...]
     │         └─ 子項可用 left/top/right/bottom 絕對定位
     │         └─ fit 屬性控制非定位子項的尺寸策略
     │
     ├─ Container
     │    └─ [單一 Control]  ⚠️ 只能有一個子項
     │         └─ 若要包多個：先用 Row/Column/Stack 包裝
     │
     └─ ResponsiveRow
          └─ [Control, ...]
               └─ 子項用 col={} 指定佔欄數
```

---

*文件版本：flet 0.82.2（docs.flet.dev）*
*整理：subagent，2026-03-22*
