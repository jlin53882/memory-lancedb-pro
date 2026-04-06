# PR5 & PR6 重新设计方案

> 基于 Flet 0.28.3 避坑经验设计

---

## PR5: 统一状态元件应用

### 当前问题
1. ❌ `ON_SURFACE_VARIANT` 不存在于 flet 0.28.3 → 应改用 `ON_SURFACE`
2. ❌ 需要验证各 View 中现有的加载/空数据/错误状态

### 设计要点

#### 1. 先修复 components.py 中的颜色错误
```python
# 修复前
color=ft.Colors.ON_SURFACE_VARIANT

# 修复后（使用已知存在的颜色）
color=ft.Colors.ON_SURFACE
# 或使用 gray/grey 颜色
color=ft.Colors.GREY
```

#### 2. 应用场景
| 场景 | 使用函数 | 验证点 |
|------|----------|--------|
| 数据加载中 | `loading_state()` | ✅ 用 `CupertinoActivityIndicator` 或 `ProgressBar` |
| 无搜索结果 | `empty_state()` | ✅ 需传 icon + title + message |
| 加载失败 | `error_state()` | ✅ 需传 retry_button 可选 |

#### 3. CacheView 中的应用位置
- **查询结果为空**: `_render_query_results()` 无结果时 → `empty_state`
- **数据加载中**: 各 panel 初始加载时 → `loading_state`
- **操作失败**: snack_bar 显示错误 → `error_state`

---

## PR6: CacheView 重构

### 设计原则（避坑）
1. ✅ **不用 ft.UserControl** → 继承 `ft.Container`
2. ✅ **Dialog 用 overlay** → `page.overlay.append(dlg)`
3. ✅ **update() 时机** → 控件已添加到 page 后再调用
4. ✅ **Scroll** → 父容器必须有高度限制
5. ✅ **ListView** → 替代 Column 处理大数据
6. ✅ **避免嵌套复杂控件** → 用 Container 组合

### 目录结构
```
cache_manager/
├── __init__.py
├── cache_actions.py      # 操作包装（已有）
├── overview_panel.py     # 统计面板
├── query_panel.py        # 查询面板
├── shard_panel.py        # 分片管理面板
└── cache_view.py         # 主视图（整合各 panel）
```

### 组件通信
```python
class CacheView(ft.Container):
    def __init__(self, page, cache_manager):
        self.page = page
        self.cache_manager = cache_manager
        super().__init__(
            expand=True,
            content=self._build_layout()
        )

    def _build_layout(self):
        # 使用 Tabs 切换各 panel
        return ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="总览", content=CacheOverviewPanel(self.page, self.cache_manager)),
                ft.Tab(text="查询", content=CacheQueryPanel(self.page, self.cache_manager)),
                ft.Tab(text="分片", content=CacheShardPanel(self.page, self.cache_manager)),
            ],
            on_change=self._on_tab_change,
        )
```

### 各 Panel 基础结构
```python
class CacheOverviewPanel(ft.Container):
    """继承 Container，避免 UserControl 问题"""

    def __init__(self, page, cache_manager):
        self.page = page
        self.cache_manager = cache_manager
        super().__init__(
            expand=True,
            padding=10,
            content=self._build_content()
        )
```

---

## 验证清单（必须检查）

- [ ] `ON_SURFACE_VARIANT` 替换为 `ON_SURFACE` 或 `GREY`
- [ ] 所有 `page.dialog =` 改为 `page.overlay.append()`
- [ ] 所有新增控件使用 `ft.Container` 而非 `ft.UserControl`
- [ ] Column/ListView 的父容器有高度限制
- [ ] 推送前用 `py_compile` 验证语法

---

## 执行顺序

1. **Phase 1**: ✅ 修复 components.py 中的颜色错误 (ON_SURFACE_VARIANT → TEXT_SECONDARY)
2. **Phase 2**: ✅ 在 CacheView 中应用 empty_state/loading_state
   - empty_state 用于查询无结果
   - SnackBar + ProgressBar 用于加载中
   - 错误通过 overview_status 显示
3. **Phase 3**: ✅ 完善 panels 目录结构（全部继承 ft.Container）

## 验证结果
- [x] pytest 171 passed
- [x] py_compile 无错误
