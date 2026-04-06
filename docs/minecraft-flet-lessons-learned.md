# Minecraft Translator Flet 踩坑指南
> 記錄 PR5~PR35 中發現的錯誤模式，避免重蹈覆轍
> 建立時間：2026-03-22｜適用版本：minecraft-translator-flet + Flet 0.28.3

---

## 一、PR 系列術語速查

| 術語 | 專案 | 內容 | 備註 |
|------|------|------|------|
| **PR5** | minecraft-translator-flet | Cache View 重構（實驗性） | 2026-03-18 |
| **PR7** | minecraft-translator-flet | cache_view UI 效能優化 | 2026-03-17 |
| **PR9** | minecraft-translator-flet | 移除靜音 pass + 強化錯誤日誌 | 2026-03-17 |
| **PR35** | minecraft-translator-flet | Phase 2 | 2026-03-21 |

---

## 二、Flet UI 常見錯誤模式

### 2.1 SnackBar 顯示問題（PR9 踩坑）

**錯誤假設**：`self.update()` 可以更新 SnackBar

**實際行為**：
- `SnackBar` 顯示後，必須呼叫 `self.page.update()`
- `self.update()` 在 Flet 0.28.3 對 SnackBar **無效**

**正確寫法**：
```python
snack = ft.SnackBar(content, duration=...)
self.page.overlay.append(snack)
snack.open = True
self.page.update()  # ← 必須用 page.update()，不是 self.update()
```

**驗證方式**：
```python
python -c "import flet as ft; help(ft.SnackBar)"
```

---

### 2.2 ft.Page() 不能無參數實例化（PR5 踩坑）

**錯誤假設**：`ft.Page()` 可以像 Python 類別一樣不帶參數呼叫

**實際行為**：
- `ft.Page()` 需要 `page` 參數
- 無參數呼叫會拋 `TypeError`

**UI 測試解決方案**：
建立 `MockPage` 物件，不依赖真实的 Flet Page：
```python
class MockPage:
    def __init__(self):
        self.overlay = []
        self.update_count = 0
    def update(self):
        self.update_count += 1

# 使用時替換
page = MockPage()
```

---

### 2.3 Icons 常數存在性未驗證（PR7 踩坑）

**錯誤假設**：`ft.Icons.FILL_OUTLINED` 存在於 Flet 0.28.3

**實際行為**：`FILL_OUTLINED` 在 Flet 0.28.3 中不存在

**正確做法**：
- 查文件確認常數存在性：`python -c "import flet as ft; print(dir(ft.Icons))"`
- 或直接用字串 `name="fill_outlined"` 而非 `ft.Icons.FILL_OUTLINED`

---

### 2.4 super().__init__() 順序問題（PR5-PR7 最常見 P0）

**錯誤模式**：
```python
class MyControl(ft.Container):
    def __init__(self, page):
        super().__init__()      # ← 順序錯誤：先呼叫 super，但 page 還沒設定
        self.page = page        # ← 這行在 super() 之後
```

**正確順序**：
```python
class MyControl(ft.Container):
    def __init__(self, page):
        self.page = page        # ← 先設定 self.page
        super().__init__()      # ← super() 最後呼叫
        self.bgcolor = ft.colors.SURFACE
```

**為什麼重要**：`super().__init__()` 內部可能需要存取 `self.page`，若順序顛倒會導致 `AttributeError`

---

### 2.5 ft.UserControl 動態掛載問題

**錯誤模式**：動態建立 `ft.UserControl` 並加入 `page.add()` 後，執行時報錯

**Flet 0.28.3 穩定寫法**：
- 避免繼承 `ft.UserControl`
- 改用 `ft.Container` 或其他 native control 作為基底類別

---

### 2.6 Container 灰色圖塊（翻譯視圖日誌區）

**症狀**：日誌區顯示灰色不可見圖塊

**排查方向**：
1. `bgcolor=None` → 改 `bgcolor="transparent"` 或明確指定顏色
2. `expand=True` 缺失 → ListView/Column 需要高度限制，加上 `expand=True`
3. `Text` 的 `color=None` → 改為明確顏色值

**確認 expand 是否需要**：
```python
# ListView 沒有 expand 的話，高度為 0，不會渲染
ft.ListView(expand=1)  # expand=1 或 expand=True
```

---

## 三、測試環境注意事項

### 3.1 必須在專案 venv 環境執行

**錯誤**：在全域環境執行 `pytest` 或 `python main.py`，導致 `ModuleNotFoundError`

**原因**：專案依賴（如 `flet`、`openpyxl`）安裝在 `.venv` 內，不在全域 Python 路徑

**正確做法**：
```powershell
cd C:\Users\admin\Desktop\minecraft_translator_flet
.\.venv\Scripts\python.exe -m pytest
# 或
.\.venv\Scripts\activate
python -m pytest
```

**每次 James 報失敗**：第一句問「有沒有在專案 venv 環境跑測試」，而不是問「有沒有清除快取」

---

## 四、版本對應關係

| Flet 版本 | minecraft-translator-flet 相容版本 |
|-----------|-----------------------------------|
| 0.28.3 | PR5-PR35（目前穩定） |
| 0.28.3 以上 | 未驗證 |

> **禁止升級 Flet 版本**（專案已固定 0.28.3）

---

## 五、GitHub / PR 工作流鐵則

### 5.1 Feature Branch 先行

**聽到「開 PR」就立刻建立 branch，不得在 main 上先實作：**
```bash
git checkout -b pr{N}/{short-description}
git push -u origin pr{N}/{short-description}
```

### 5.2 PR 完成後才允許合併

每顆 PR 必須經過：
1. Phase 0 盤點回報
2. Phase 1 實作與 Validation checklist 確認
3. Commit + Push
4. 才建立 PR

---

## 六、相關檔案索引

| 主題 | 檔案路徑 |
|------|---------|
| PR5-PR7 設計稿 | `docs/pr/PR5-PR7-*.md` |
| FTB Quest 抽取流程 | `docs/ftbquest-extraction.md` |
| SnackBar 修復驗證 | `workspace/pr10_*.md` |
| Flet 0.28.3 避坑完整版 | `docs/flet-ui-0283-design-audit.md` |

---

*本檔案由 SA-3 指令分析 + SA-4 行為驗證產生（2026-03-22）*
*目的：將踩坑紀錄結構化為可查閱的指南，杜絕同類錯誤重複發生*
