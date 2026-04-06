# LESSONS_LEARNED — 做 X 之前要先查 Y

> 目的：系統化整理所有踩坑經驗，讓未來的自己能快速找到「做某件事之前要注意什麼」。
> 本檔案儘量填入已驗證的具體細節；仍需 James 確認的項目標記 [TODO]。

---

## two_project 踩坑

> 適用版本：two_project（Flet 0.82.2）

### 🔴 UI / Flet 灰畫面相關

#### Flet 灰畫面問題（Gray Screen / No Response）

**觸發情境**：操作 two_project UI 時，整個畫面或某區塊變灰、完全無回應，且沒有任何錯誤訊息。

**問題根因（已知）**：
1. `build()` 裡才設定核心 layout，導致初始化時頁面空白
2. `did_mount()` 沒包 `try/except`，例外被吞掉，畫面卡住
3. 背景執行緒（`run_bg`）直接呼叫 `page.update()`，在非 UI thread 更新導致例外
4. `expand + scroll + 巢狀 expand` 高風險組合，容易讓 Container 高度為 0

**預防（做之前要先查）**：
- 查 `FLET_DEBUG_STRATEGY.md` 的灰畫面排查 SOP
- 查 `FLET_FIXES.md` 的灰塊防呆清單
- 任何 View 的 layout 應在 `__init__` 完成，不要依賴 `build()` 掛內容
- 所有 `did_mount()`、`on_click`、背景任務都必須包 `try/except`

**止血 SOP（已驗證）**：
1. 設定 `page.on_error` → 寫入 `exports/error.log` + SnackBar
2. 各 View 的 `did_mount()` 包 `try/except` → `log_exception()` + SnackBar
3. 背景任務統一走 `run_bg(page, work, on_done, on_error)`，錯誤時 `on_error` 必須 `log_exception()` + SnackBar
4. 避免在 thread 裡直接 `page.update()`，回到 UI thread 再做

**Dev overlay（最小可視化）**：
- 可加 `event_seq` / `last_event` 機制（`src/utils/debug_trace.py`）
- 每個 handler 進來先 `mark_event("View.action")` 記錄事件序號
- last_event 沒變 → 事件根本沒進來（檢查 disabled/遮罩/on_click 綁定）
- last_event 有變但沒結束 → 卡在 handler 裡（看 error.log）

---

#### Flet 0.82.2 Dialog 行為（與 0.28.3 不同）

**觸發情境**：從 minecraft_translator_flet（Flet 0.28.3）移植程式碼到 two_project（Flet 0.82.2），使用 Dialog 元件。

**問題**：
| 錯誤寫法 | 正確寫法（0.82.2） |
|---------|----------------|
| `page.open(dlg)` | `page.show_dialog(dlg)` |
| `page.close()` | `page.pop_dialog()`（不吃參數）|

**預防**：跨版本移植 Dialog 程式碼前，先查 `flet-0822-vs-0283.md` 的 Dialog 章節。

---

#### Flet 0.82.2 Container 沒有 scroll 參數

**觸發情境**：從 0.28.3 移植時直接寫 `ft.Container(scroll=ft.ScrollMode.AUTO, ...)`。

**問題**：Flet 0.82.2 的 `Container` **沒有** `scroll` 參數，直接設會導致滾動失效（畫面灰塊）。

**正確做法（0.82.2）**：
```python
# ❌ 錯誤：0.82.2 Container 沒有 scroll 參數
ft.Container(height=300, scroll=ft.ScrollMode.AUTO, content=...)

# ✅ 正確：用 Column 或 ListView 包滾動內容
ft.Container(height=300, content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[...]))
```

**預防**：跨版本移植前，先查 `flet-0822-vs-0283.md` 的 Container scroll 章節。

---

#### Flet 0.82.2 大量新 API（0.28.3 不存在）

**觸發情境**：參考 Flet 官方文件（docs.flet.dev，版本 0.82.2）寫程式碼，卻用在 0.28.3 的 minecraft_translator_flet。

**問題**：文件（0.82.2）與實際原始碼（0.28.3）有重大差異，以下 API 在 0.28.3 **不存在**：

| 0.82.2 新 API | 0.28.3 是否有 |
|--------------|-------------|
| `ResponsiveRow` | ❌ 沒有 |
| `Container.ink` / `ink_color` | ❌ 沒有 |
| `Container.blur` | ❌ 沒有 |
| `Container.blend_mode` | ❌ 沒有 |
| `Container.color_filter` | ❌ 沒有 |
| `Container.foreground_decoration` | ❌ 沒有 |
| `Container.ignore_interactions` | ❌ 沒有 |
| `Row.tight` / `Row.intrinsic_height` | ❌ 沒有 |
| `Column.tight` / `Column.intrinsic_width` | ❌ 沒有 |
| `Row.run_spacing` / `Column.run_spacing` | ❌ 可能沒有 |

**預防**：
- 查 `flet-0822-vs-0283.md` 的綜合差異表
- 查 `flet-0822-section2-layout.md` 的「✅ 已驗證 vs ❌ 待驗證」清單
- **嚴禁**在 minecraft_translator_flet（0.28.3）使用 ResponsiveRow

---

### 🟡 架構 / 設計相關

#### [TODO] two_project UI 重構的已知問題

**觸發情境**：進行 two_project UI 重構。

**問題**：（需要 James 補充具體重構過程中遇到的坑）

**預防**：重構前先讀 `docs/AI_WORKFLOW_MANUAL.md` 的 two_project 相關章節。

---

## minecraft_translator_flet 踩坑

> 適用版本：minecraft-translator-flet（Flet 0.28.3）

### 🔴 PR / 設計相關

#### reverse_index dedup 的三大 bug（PR #40/#41/#42）

**觸發情境**：修改 `kubejs_translator_clean.py` 的 dedup 邏輯。

**問題（已驗證）**：

**Bug 1 — 效能退化**
- `final_tw_lookup` 和 `reverse_index` 在 `groups` 迴圈**每次迭代都重建**
- 正確做法：在迴圈外一次計算，迴圈內重複使用

**Bug 2 — 非確定性過濾**
- 使用 `reverse_index[v][0]` 取 key
- `rglob()` 的順序在 Windows 上不穩定，導致每次執行結果不同
- 正確做法：改為 `k not in reverse_index[v]`（遍歷 key 而非取第一個值）

**Bug 3 — 語意錯配** ⚠️（最嚴重）
- `reverse_index` 的值是**中文明值**（從 `zh_tw.json` 建立）
- 但比對的目標是**英文**（`pending_en`）
- 中文字不可能匹配英文字串，導致 dedup 幾乎**永不命中**
- 正確做法：比對英文 key，而非中文字串值

**預防**：修改 dedup 邏輯前，先完整讀取 `kubejs_translator_clean.py` 的現有實作，並對照 PR #40/#41 的 commit 變更。

---

#### [TODO] kubejs_translator_clean 的效能問題

**觸發情境**：執行 kubejs_translator_clean.py 時速度慢。

**問題**：（需要 James 補充具體瓶頸是什麼）

**預防**：修改前先跑一次 profiling，確認瓶頸點。

---

### 🟡 翻譯流程相關

#### COLOR_PATTERN regex 範圍過寬

**觸發情境**：新增 Minecraft 顏色碼檢查時，直接參考網路或舊程式碼的 regex。

**問題**：
- `COLOR_PATTERN` 的 `[a-v]` 範圍把無效碼（`&g`, `&p`, `&s` 等）也當合法顏色
- Minecraft 官方格式碼只有 `[0-9a-fk-orx]`

**正確做法**：
```python
# ❌ 錯誤：[a-v] 包含無效碼
COLOR_PATTERN = re.compile(r'&[a-v]')

# ✅ 正確：官方格式碼
COLOR_PATTERN = re.compile(r'&[^0-9a-fk-orx\s\\#]')
```

**預防**：實作顏色檢查前，先查 Minecraft Wiki 官方格式碼規格。

---

#### [TODO] 翻譯流程中已知的其他坑

**觸發情境**：修改翻譯流程相關程式碼。

**問題**：（需要 James 補充）

**預防**：修改前先查 `PROJECT_MINECRAFT_TRANSLATOR.md`。

---

### 🟡 Flet UI 相關（minecraft_translator_flet）

#### SnackBar 顯示問題（PR9 踩坑）

**觸發情境**：在 Flet 0.28.3 中使用 SnackBar 顯示操作結果。

**問題**：
- `SnackBar` 顯示後，必須呼叫 `page.update()`
- `self.update()` 對 SnackBar **無效**

**正確寫法**：
```python
snack = ft.SnackBar(content, duration=...)
self.page.overlay.append(snack)
snack.open = True
self.page.update()  # ← 必須用 page.update()，不是 self.update()
```

**預防**：任何 SnackBar 操作前，先查 `minecraft-flet-lessons-learned.md` 的 SnackBar 章節。

---

#### ft.Page() 不能無參數實例化（PR5 踩坑）

**觸發情境**：寫測試程式時想建立一個假的 Page 物件。

**問題**：`ft.Page()` 需要 `page` 參數，無參數呼叫會拋 `TypeError`。

**正確做法**：建立 `MockPage` 物件：
```python
class MockPage:
    def __init__(self):
        self.overlay = []
        self.update_count = 0
    def update(self):
        self.update_count += 1
```

---

#### Icons 常數存在性未驗證（PR7 踩坑）

**觸發情境**：使用 `ft.Icons.FILL_OUTLINED` 等常數。

**問題**：`FILL_OUTLINED` 在 Flet 0.28.3 中**不存在**。

**正確做法**：
- 先用 `python -c "import flet as ft; print(dir(ft.Icons))"` 確認常數存在
- 或直接用字串 `name="fill_outlined"` 而非 `ft.Icons.FILL_OUTLINED`

---

#### super().__init__() 順序問題（PR5-PR7 最常見 P0）

**觸發情境**：自訂 `ft.Container` 子類，在 `__init__` 裡存取 `self.page`。

**問題**：`super().__init__()` 在 `self.page = page` **之前**呼叫，導致 `AttributeError`。

**正確順序**：
```python
class MyControl(ft.Container):
    def __init__(self, page):
        self.page = page        # ← 先設定 self.page
        super().__init__()      # ← super() 最後呼叫
        self.bgcolor = ft.colors.SURFACE
```

**預防**：任何繼承 `ft.Container` / `ft.UserControl` 的自訂類，先查 `minecraft-flet-lessons-learned.md` 的章節 2.4。

---

#### ft.UserControl 動態掛載問題

**觸發情境**：動態建立 `ft.UserControl` 並加入 `page.add()`。

**問題**：在 Flet 0.28.3 中容易出錯。

**正確做法**：避免繼承 `ft.UserControl`，改用 `ft.Container` 作為基底類別。

---

#### Container 灰色圖塊（翻譯視圖日誌區）

**觸發情境**：日誌區顯示為灰色不可見圖塊。

**排查方向**：
1. `bgcolor=None` → 改 `bgcolor="transparent"` 或明確指定顏色
2. `expand=True` 缺失 → `ListView`/`Column` 需要高度限制，加上 `expand=True`
3. `Text` 的 `color=None` → 改為明確顏色值

**預防**：任何滾動區塊先確認 `expand=True` 和明確背景色。

---

### 🟡 測試環境相關

#### 必須在專案 venv 環境執行（PR5-PR35 通則）

**觸發情境**：在全域環境執行 `pytest` 或 `python main.py`。

**問題**：導致 `ModuleNotFoundError`（flet、openpyxl 等只在 .venv 內）。

**正確做法**：
```powershell
cd C:\Users\admin\Desktop\minecraft_translator_flet
.\.venv\Scripts\python.exe -m pytest
```

**預防**：James 報失敗時，第一句問「有沒有在專案 venv 環境跑測試」，不要先問快取。

---

## Agent 操作踩坑

### 🟢 架構 / 流程相關

#### Sub-agent 該開沒開

**觸發情境**：大型任務在主線跑太久，導致 context 污染嚴重或 timeout。

**正確做法**：
- 任務評估 > 5 分鐘或 > 3 步 → 應該開 sub-agent
- 批量任務 > 3 件 → 優先拆開
- Context > 80k tokens → 優先拆開
- Sub-agent 正在跑時，不再隨意追加新任務

**預防**：
- 收到任務時先評估複雜度
- 查 `AGENTS.md` 的 Sub-Agent Policy 章節
- 模型統一用 `minimax-portal/MiniMax-M2.7`，timeout 預設 600 秒

---

#### Context 膨脹未及時處理

**觸發情境**：對話太長導致效能下降、回應變慢。

**正確做法**：
- Context > 60% 就應該考慮 `/compress`
- Context > 80k tokens 主動建議 `/reset`
- 每次結束對話前檢查是否有新決策需要寫入

**預防**：
- 定時用 `session_status` 檢查 context 使用量
- 大檔讀取用 `Select-String` 定位 → 小範圍 read（±20 行）
- 禁止對 `dist/`、`node_modules/`、整個 workspace 做暴掃

---

#### 記憶管理問題

**觸發情境**：寫入新記憶時與舊記憶衝突、記憶污染、或應該寫卻沒寫。

**正確做法**：
- 寫入前先做相似記憶搜尋
- 找到高度相似舊記憶時，詢問 James 更新舊的還是保留兩條
- 結論取代舊結論時，舊條目標 `[Deprecated]` 再立新結論
- 每條記憶必填版本/環境欄位

**預防**：
- 查 `memory/decisions.v2.md`（唯一 canonical 決策來源）
- ENOENT/路徑錯誤：先 recall → 再 QMD → 最後才搜程式碼
- 禁止直接硬刪舊記憶

---

#### [TODO] Sub-agent 判斷不夠精準的經驗

**觸發情境**：需要開 sub-agent 時沒開，或不該開時開了。

**問題**：（需要 James 補充具體例子）

**預防**：（需要 James 補充）

---

#### [TODO] 記憶管理的其他問題

**觸發情境**：記憶系統使用過程中遇到的問題。

**問題**：（需要 James 補充）

**預防**：（需要 James 補充）

---

## OpenClaw / 系統操作踩坑

### 🟡 系統設定相關

#### memory-lancedb-pro 設定三坑

**觸發情境**：設定 memory-lancedb-pro plugin。

**問題**：
1. `plugins.load.paths` 要用**絕對路徑**（相對路徑找不到 plugin）
2. `embedding.apiKey` 仍需非空值（可填 dummy）
3. Windows/PowerShell 寫 JSON 時注意反斜線雙重轉義

**預防**：設定前先查 `decisions.v2.md` 的 `D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG`。

---

#### Gateway 重啟連不上

**觸發情境**：執行 `openclaw gateway restart` 後 RPC probe failed / token mismatch。

**根因**：Scheduled Task 指向錯誤來源的 openclaw（可能指向 pnpm shim，而 pnpm 已移除）。

**正確修法**：
1. 確保 `openclaw` 由 `npm install -g openclaw@latest` 安裝
2. `gateway.cmd` 固定呼叫 `C:\Users\admin\AppData\Roaming\npm\openclaw.cmd`
3. 移除 `OPENCLAW_GATEWAY_TOKEN` 環境變數覆蓋

**預防**：Gateway restart 前必先通知 James（重啟後 agent 會暫時離線）。

---

#### [TODO] 其他 OpenClaw 操作坑

**觸發情境**：使用 OpenClaw 過程中遇到的問題。

**問題**：（需要 James 補充）

**預防**：（需要 James 補充）

---

## 快速查詢索引

| 我要做... | 先查... |
|-----------|--------|
| 修改 two_project Flet UI | `docs/FLET_DEBUG_STRATEGY.md` + `docs/FLET_FIXES.md` |
| 跨 Flet 0.28.3 ↔ 0.82.2 移植 | `docs/flet-0822-vs-0283.md` + `docs/flet-0822-knowledge-index.md` |
| 修改 kubejs_translator_clean dedup | `LESSONS_LEARNED.md`（本檔案的 minecraft 部分）+ PR #40/#41 |
| 新增 minecraft_translator_flet PR | `memory/minecraft-flet-lessons-learned.md` |
| 設定 memory-lancedb-pro | `memory/decisions.v2.md` 的 `D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG` |
| 開 Sub-agent | `AGENTS.md` 的 Sub-Agent Policy 章節 |
| Context 爆炸要壓縮 | `memory-compress` skill + `AGENTS.md` 的 [LEARNED_RULES] |
| 精準讀大檔 | `memory/decisions.v2.md` 的 `P-2026-02-15-PRECISE-READING-WINDOW` |
| PowerShell 寫中文檔 | 一律用 `write` tool（自動 UTF-8），嚴禁用 redirect |

---

## [TODO] 待 James 確認的項目

以下項目需要 James 補充具體細節才能完整填寫：

1. **two_project UI 重構的已知問題** — 具體遇到什麼坑？
2. **kubejs_translator_clean 的效能問題** — 具體瓶頸是什麼？
3. **翻譯流程中已知的其他坑** — 除了 dedup 和 COLOR_PATTERN 之外？
4. **Sub-agent 判斷不夠精準的經驗** — 哪幾次該開沒開？
5. **記憶管理的其他問題** — 具體是什麼問題？
6. **其他 OpenClaw 操作坑** — 還有哪些？

---

*最後更新：2026-03-25*
