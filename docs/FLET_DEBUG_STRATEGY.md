# two_project — Flet「灰畫面難除錯」整合建議（不複雜化版）

> 目標：把「灰畫面/沒訊息」變成「一定看得到錯（SnackBar + error.log）」；在不把專案搞複雜的前提下，建立可持續的除錯/診斷路徑。
>
> 依據：two_project/README.md 的硬規格（SnackBar 統一、async_runner、桌面模式方向）

---

## 0) 結論：可行，而且應該用「兩層」策略

- **第 1 層（止血）**：任何錯誤都要「可見 + 可追溯」
  - 使用者看到 SnackBar（成功/失敗/哪裡出錯）
  - 開發者拿到 `error.log` 的 traceback（能定位檔案/行號）

- **第 2 層（預防再犯）**：減少 Flet 容易灰掉的寫法
  - Container/View 的 layout 在 `__init__` 建好（不依賴 `build()` 來掛內容）
  - 背景任務只能算資料，UI 更新回 UI thread

這樣不需要導入大型 state 管理/複雜框架，也不需要「到處加 debug print」。

---

## 1) 設計/架構觀點（brainstorm agent 摘要）

### P1（MVP 必做，先讓錯誤不再消失）
1. **async_runner 統一錯誤攔截**
   - 所有重 IO/耗時操作都經過同一個 wrapper
   - wrapper 內 `try/except`：
     - 顯示 SnackBar（錯誤摘要）
     - 記錄 exception（含 traceback）

2. **SnackBar 錯誤回饋分級（success/info/error）**
   - 符合你規格：所有輸入檢核失敗、輸出成功/失敗都用 SnackBar 統一
   - dev 模式可加「查看詳情」/ 或提示去看 error.log

3. **Safe update（避免 update 異常導致整頁灰）**
   - 封裝 `safe_update(page)`，update 失敗也要記 log

### P2（穩定後加，提升診斷效率但不增加負擔）
4. **Dev overlay（只在 DEBUG 模式顯示）**
   - 顯示：目前 view 名、最後一個事件、最近 1~3 行 log
   - 加強：**事件序號（event_seq）+ 最後事件紀錄（last_event）**
     - 每個 handler 一進來就先記一筆：`last_event = "view.action#N"`
     - 同步寫入 log，overlay 也顯示
     - 目的：快速區分「事件根本沒進來」vs「進來但卡住」

5. **啟動時控件樹健康檢查（可選）**
   - 檢查顯而易見的結構問題（例如 content=None / 重複 key）

### P3（進階可選，不急）
6. 結構化 log（JSONL）
7. 切頁埋點（view_switch）
8. Crash recovery dump（遇到未捕獲例外時 dump 狀態）

> MVP 路線（1~3 步）：
> 1) async_runner + SnackBar 分級
> 2) safe_update +（可選）Dev overlay
> 3)（可選）結構化 log + 啟動檢查

---

## 2) 實作建議（code agent 摘要，最小 patch 路線）

### 優先順序
1) **`page.on_error` → 寫入 error.log + SnackBar（立刻止血）**
2) **所有事件入口加 try/except + log**（did_mount / on_click / run_bg / thread）
3) **Container/View 不依賴 build()**（layout 在 __init__ 建好）
4) **Debug banner/overlay（最小可視化）**
5) **UI thread 更新規則**（背景不直接 update）

### 最小 patch 方向（不複雜化版本）
- 新增 1 個小工具檔：`src/utils/error_log.py`
  - `log_exception(name, ex)`：追加寫入 `exports/error.log`
  - （可選）`log_text(name, text)`：記錄切頁/事件

- 在 app 入口（`src/app.py` 或 `src/main.py`）設定：
  - `page.on_error = ...`（任何 UI 層錯誤都進 log + SnackBar）

- 在每個 view：
  - `did_mount()` 包 try/except → `log_exception('xxx.did_mount', ex)` + SnackBar
  - 所有 `on_click/on_change` 入口也同樣包

- 背景任務：
  - 統一用 `run_bg(page, work, on_done, on_error)`
  - `on_error` 一定 `log_exception(...)` + SnackBar
  - 不要在 thread 裡直接 `page.update()`；回到 UI thread 再做

### 驗證方式（固定）
- `uv run src/main.py`
- 操作到會出問題的路徑
- 期待看到：
  1) SnackBar 出現「發生錯誤／已記錄」
  2) `exports/error.log` 最後一段有 traceback（可定位）

---

## 3) 跟 two_project README 規格如何對齊（不增加複雜度）

### 必守規格（你已定義）
- **所有輸入檢核失敗** → SnackBar（error）
- **所有輸出成功/失敗** → SnackBar（success/error）
- **所有重 IO** → async_runner / run_bg（不阻塞 UI）

### 建議的最小一致性規範（寫進 README Phase 3 或 2.5 都可）
- 每個 View 必備：
  - `__init__` 設定 `self.content`（不要靠 build 掛 layout）
  - `did_mount` 必包 try/except + log
- 背景任務必走：`run_bg`
- 全站錯誤輸出：`exports/error.log`

---

## 4) 建議落地順序（不重工、不擴散）

### Step 1（1 小時內能看到效果）
- 把 `page.on_error` + `exports/error.log` 正式化
- 把 3 個最常灰的 view（Work/Portfolio/Practice）在 `did_mount` 加 try/except + log + SnackBar

### Step 2（把灰畫面根因封掉）
- 把任何 `Container` view 的 layout 改成只在 `__init__` 設 `self.content`
- 清掉依賴 `build()` 才設定 `self.content` 的寫法

### Step 3（Debug 可開關，平常不吵）
- 加一個 DEBUG 開關（環境變數或 settings）
- DEBUG=1 才顯示 overlay / banner / 更詳細 log

---

## 5) 不建議現在做的事（會讓專案變複雜）

- 立刻導入大型全域 state 管理（Redux/MobX 類）
- 到處加大量 print、或把每個 control 都包一層自訂 class
- 先做完整自動化測試框架（README 也說 tests 放最後）

---

## 6) 加強建議：事件序號（event_seq）+ 最後事件（last_event）【你補充的關鍵點】

這個很值得加，而且不會讓架構變複雜。

### 為什麼有效
很多「按了沒反應」其實是：
- 事件根本沒進 handler（按鈕 disabled、被遮罩、on_click 沒綁、control 沒渲染在樹上）
- 或進來後卡在某段（IO 卡住、死鎖、例外被吞）

有 `event_seq` / `last_event` 你可以一眼判斷是哪一類。

### 最小落地（建議）
- 放在 `src/utils/debug_trace.py`（小檔，2 個全域變數 + 2 個函式即可）
- 每個 handler 一進來先呼叫：
  - `mark_event("WorkView.save")` → 回傳字串 `WorkView.save#12`
  - 同步：
    - `log_text("event", last_event)` 寫入 `exports/error.log`
    - overlay 顯示 `last_event`

### 判讀方式（固定 SOP）
- last_event 沒變：事件沒進來 → 檢查綁定/disabled/遮罩/可見性
- last_event 有變但沒結束：卡在 handler → 看 error.log、加更細分 mark

---

## 7) 你要我接著做什麼（不覆蓋 README）

我可以在 `two_project` 內新增一份 `docs/debugging.md`（或放 workspace），並把 Step 1 + 事件序號機制寫成可直接套用的最小 patch 清單（改哪些檔/加哪些函式/驗證步驟）。
