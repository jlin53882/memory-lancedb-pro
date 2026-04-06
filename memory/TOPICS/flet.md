# Flet 桌面應用 知識索引
> 蒸餾日期：2026-03-25
> 來源：memory/flet-0822-*.md 系列（共19個檔案）

---

## 核心知識點

1. **Flet 版本標籤** - 目前使用 `flet:0.82.2`，資料來源為 https://docs.flet.dev。- 來源：flet-0822-KNOWLEDGE-INDEX.md

2. **Pubsub 發布訂閱** - `page.pubsub.subscribeAll()` / `page.pubsub.send_all()`，跨頁面通訊機制。Cookbook 有完整範例。- 來源：flet-0822-KNOWLEDGE-INDEX.md

3. **Async Apps（非同步）** - Flet 支援 `async def` handler，避免阻斷主執行緒。- 來源：flet-0822-agent-cookbook.md

4. **Client Storage** - `page.client_storage` 可存 key-value，適合持久化使用者設定。- 來源：flet-0822-agent-cookbook.md

5. **自訂控制項（Custom Controls）** - 可擴展既有控制項，加入 custom properties。- 來源：flet-0822-agent-cookbook.md

6. **page.on_error 無法捕獲 UI handler 異常** - 驗證：Flet API `ft.Page()` 無法不帶參數實例化。破壞性失敗必須 raise，嚴禁 `return {}`。- 來源：AGENTS.md [LEARNED_RULES]

7. **flet.app() 啟動方式** - `view: Optional[AppView] = AppView.FLET_APP`，預設啟動 Flet_APP 視窗。- 來源：venv_flet_full_learning.md

8. **Theme 設定** - `page.theme = Theme(...)` 可設定 primary color、font 等。- 來源：flet-0822-section1-startup-core.md

9. **部署方式** - `flet build` 打包桌面執行檔，`flet publish` 發布 Web。- 來源：flet-0822-section5-deploy-diagnostic.md

10. **TextField / DataTable** - `TextField()` 可設 `on_change`，`DataTable` 支援排序。- 來源：flet-0822-section4-input.md

---

## 常見踩坑

1. **無法用瀏覽器自動化工具控制 Flet UI** - PinchTab、OpenClaw browser 工具都無法操控 Flet Web 或桌面版的按鈕/元素。解法：需在 Flet 程式碼中加 `autoid` 測試鉤子，或用 `pywinauto` 等桌面自動化工具。- 來源：2026-03-17-flet-automation.md

2. **PinchTab 在 Windows 無頭模式會失敗** - 實例卡在 starting 狀態，應避免在 Windows 使用，改用 OpenClaw 內建瀏覽器。- 來源：TOOLS.md

3. **Flet Web 無障礙支援有限** - 元素無法被自動化工具識別，無法點擊按鈕。- 來源：2026-03-17-flet-automation.md
