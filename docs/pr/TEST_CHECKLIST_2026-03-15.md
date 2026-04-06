# UI 测试验证工作表

> 日期：2026-03-15
> 测试命令：
> - `cd C:\Users\admin\Desktop\minecraft_translator_flet`
> - `.venv\Scripts\python test_main.py` (启动 web 测试)
> - `.venv\Scripts\python -m pytest -q` (单元测试)

---

## 一、单元测试 (pytest)

```bash
.venv\Scripts\python -m pytest -q
```

**预期结果：** 171 passed

---

## 二、UI 功能测试

### 1. 启动测试
- [ ] 启动 `.venv\Scripts\python test_main.py`
- [ ] 访问 http://127.0.0.1:8550
- [ ] 检查各 View 是否正常加载

### 2. CacheView 测试 (重点)

#### 2.1 进度条 SnackBar
- [ ] 点击「重新载入」按钮
- [ ] 确认底部显示 SnackBar 进度条
- [ ] 确认操作完成后进度条消失
- [ ] 确认「重建索引」也有进度条

#### 2.2 空状态显示
- [ ] 进入 CacheView → 查询页面
- [ ] 输入不存在的关键词搜索
- [ ] 确认显示 empty_state (无搜索结果)

#### 2.3 颜色验证
- [ ] 检查 CacheView 总览面板颜色正常（无报错）
- [ ] 检查 QuickJump 面板颜色正常

### 3. 其他 View 快速检查
- [ ] TranslationView 正常加载
- [ ] ConfigView 正常加载
- [ ] RulesView 正常加载

---

## 三、今天修改的文件清单

| Commit | 文件 | 修改内容 |
|--------|------|----------|
| `07c1bf2` | panels/*.py | 全部继承 ft.Container |
| `86849e6` | cache_view.py | empty_state 应用到查询无结果 |
| `b07a60d` | theme.py, test_*.py | 添加 TEXT_SECONDARY_200 |
| `6f93823` | components.py, quick_jump.py | 统一使用 theme.py |
| `5c81bcc` | components.py, quick_jump.py | ON_SURFACE_VARIANT → GREY |
| `bd1298e` | overview_panel.py, extractor_view.py, cache_actions.py | 修复 Flet 避坑 |
| `1123f89` | cache_actions.py | ThreadPoolExecutor 避免阻塞 |

---

## 四、验证要点

### 颜色问题
- ❌ 之前：`ft.Colors.SURFACE_VARIANT` → 报错
- ✅ 现在：`theme.TEXT_SECONDARY` (GREY)

### 进度条
- ❌ 之前：Banner 不显示（阻塞 UI）
- ✅ 现在：SnackBar + ThreadPoolExecutor 显示正常

### Dialog
- ❌ 之前：`page.dialog =` (旧写法)
- ✅ 现在：`page.overlay.append()`

---

## 五、测试检查清单

- [ ] pytest 171 passed
- [ ] web 启动无报错
- [ ] CacheView 查询无结果显示 empty_state
- [ ] 点击重新载入显示 SnackBar 进度条
- [ ] QuickJump 面板颜色正常
- [ ] overview_panel 颜色正常
