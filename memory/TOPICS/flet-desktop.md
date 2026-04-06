# Flet 桌面應用 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/

---

## 核心知識點

1. **版本：0.82.2 為目前標準（2026-03-22 建檔）**
   - 內容：Flet 0.82.2 API 文件已從 docs.flet.dev 完整抓取，共 19 個檔案約 229KB。與 0.28.3 有若干破壞性變更
   - 來源：flet-0822-KNOWLEDGE-INDEX.md

2. **`ft.run()` 取代 `ft.app()` 成為 0.82.2 標準寫法**
   - 內容：`flet create` scaffold 預設用 `ft.run(main)`，但 `ft.app()` 仍可正常運作。兩者皆為 blocking call
   - 來源：flet-0822-section1-startup-core.md

3. **BasePage / Page / MultiView 三層架構（0.82.2 新增）**
   - 內容：`BasePage` 為 abstract base，`Page` 繼承它管理 session，`MultiView` 支援多視圖。0.28.3 無此分層
   - 來源：flet-0822-section1-startup-core.md

4. **View 是最上層容器（相當於 0.28.3 的隱性 page 概念）**
   - 內容：View 是 Page 的根容器，等同於一個「畫面/Screen」，可設定 route、appbar、navigation_bar 等
   - 來源：flet-0822-section1-startup-core.md

5. **Desktop 部署：`flet run`（CLI）而非 `ft.run()` 參數**
   - 內容：Platform 是 CLI 參數切換（`flet run` 桌面 / `flet run --web` 瀏覽器），`ft.run()` 本身無 platform 參數
   - 來源：flet-0822-section5-deploy-diagnostic.md

6. **SnackBar 新寫法：`page.show_dialog(ft.SnackBar(...))`**
   - 內容：0.82.2 官方推薦用 `page.show_dialog()` 顯示 SnackBar，取代舊版直接在 controls 添加的方式
   - 來源：flet-0822-section5-deploy-diagnostic.md

7. **Pubsub 機制可用於跨 Page 狀態同步**
   - 內容：Cookbook 中有完整 PubSub 範例，適用於有多個 session 或視圖的應用
   - 來源：flet-0822-agent-cookbook.md

8. **環境變數覆蓋：`FLET_SERVER_PORT`、`FLET_SERVER_IP`、`FLET_ASSETS_DIR`**
   - 內容：`ft.run()` 支援環境變數覆蓋 CLI 設定
   - 來源：flet-0822-section1-startup-core.md

9. **GestureDetector 支援複雜手勢（拖放、縮放等）**
   - 內容：Controls A-E / F-M 中有對應文件，適用於自訂互動場景
   - 來源：flet-0822-agent-controls-fm.md

10. **部署方式：`flet publish` 可發布為可攜執行檔**
    - 內容：0.82.2 支援 `flet publish` 打包桌面應用
    - 來源：flet-0822-section5-deploy-diagnostic.md

---

## 常見踩坑

1. **`page.on_error` 無法捕獲 UI handler 異常**
   - 問題：`page.on_error` 只能捕獲 page-level 錯誤，UI handler（如按鈕點擊）中的異常它捕不到
   - 解法：每個 handler 內部自己加 try/except，不要依賴 `page.on_error`
   - 來源：AGENTS.md [LEARNED_RULES]

2. **`ft.Page()` 無法不帶參數實例化**
   - 問題：Flet Page 需要綁定到實際的 Flet 應用，無法像一般物件那樣直接 `ft.Page()` 建立
   - 解法：所有 Page 操作都透過 `page: ft.Page` 參數傳入，在 `main(page)` 裡處理
   - 來源：AGENTS.md [LEARNED_RULES]

3. **0.82.2 vs 0.28.3 破壞性變更**
   - 問題：BasePage 分層、View 角色改變、`ft.run()` vs `ft.app()` 差異、`export_asgi_app` 參數等
   - 解法：開發前先確認目標版本，差異文件見 `docs/flet-0822-vs-0283.md`
   - 來源：flet-0822-section1-startup-core.md

4. **大量中文寫入嚴禁 PowerShell redirect**
   - 問題：PowerShell redirect / `Set-Content` / `Out-File` 寫入中文會截斷或乱码
   - 解法：統一用 `write` tool（自動 UTF-8）
   - 來源：AGENTS.md [LEARNED_RULES]
