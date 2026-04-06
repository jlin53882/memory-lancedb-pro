# OpenClaw 設定 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/

---

## 核心知識點

1. **Gateway 重啟高風險：必先通知家豪並等確認**
   - 內容：所有 Gateway restart 必須先告知 James（含「重啟後 agent 會暫時離線」預警），嚴禁默默重啟；重啟後由家豪手動執行
   - 來源：decisions.v2.md（[P-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM]）

2. **Gateway restart SOP：重啟前建一次性 cron 驗證**
   - 內容：建立 cron job（20s 後執行）驗證重啟後 RPC probe 是否 ok；避免「CLI 回報失敗但已重啟」的誤判
   - 來源：2026-03-03-gateway-restart-sop.md

3. **每日更新 cron 採 B 方案（拆成兩個 job）**
   - 內容：Job 1（12:00）執行 update + restart（NO_REPLY）；Job 2（12:02）驗證版本+gateway status。避免重啟導致通知切斷
   - 來源：decisions.v2.md（[D-2026-02-25-DAILY-UPDATE-CRON-B]）

4. **SecretRef 模式：密鑰不放明文**
   - 內容：使用 `{ source: "env", provider: "default", id: "OPENAI_API_KEY" }`，勿在 config 放明文。CLI：`openclaw secrets reload` / `audit` / `configure`
   - 來源：decisions.v2.md + AGENTS.md

5. **`tools.profile: full` 讓工具完整可用（messaging 模式限制多）**
   - 內容：Discord/Telegram 訊息工具需要 `tools.profile = full` 才完整；`messaging` 模式工具受限。改完後需 restart 才生效
   - 來源：2026-03-03-gateway-restart-sop.md

6. **Sub-agent 策略：預設可開，hard limit 10 顆**
   - 內容：觸發條件：>5 分鐘、>3 件批量、>80k context。預設模型 M2.7；timeout → 立即切 M2.5 fallback
   - 來源：decisions.v2.md（[P-2026-03-21-SUBAGENT-STRATEGY]）

7. **精準讀檔策略：先定位再小範圍讀**
   - 內容：遇到 ENOENT 或路徑解析錯誤，先 recall 確認路徑，再縮到單一目標驗證，不全文掃描
   - 來源：decisions.v2.md（[P-2026-02-28-PRECISE-READ-STRATEGY]）

8. **memory-lancedb-pro 設定三坑：絕對路徑 / apiKey / JSON 轉義**
   - 內容：設定 dbPath 必須用絕對路徑、apiKey 不可有前後空白、JSON 字串內需正確轉義反斜槓
   - 來源：decisions.v2.md（[D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG]）

9. **Brave Search API 配額告警**
   - 內容：接近每月 2000 次上限時主動通知 Discord #監控警告（channel_id:1476866274628997231）
   - 來源：2026-03-05-safe-merge.md context

10. **Gateway Hot Reload 模式設定**
    - 內容：`gateway.reload.mode`：off | hot（支援項目即時套用）| restart（設定變更觸發全重啟）| hybrid。可 hot-apply：system prompt、model 選擇、tool config
    - 來源：2026-03-04-openclaw-config.md（relevant-memories 萃取）

---

## 常見踩坑

1. **Gateway restart 造成通知鏈路中斷**
   - 問題：重啟時 agent 短暫離線，若沒有驗證 cron 可能誤判為成功
   - 解法：拆成兩個 cron job，B 方案驗證，結果 announce 到監控群
   - 來源：decisions.v2.md（[D-2026-02-25-DAILY-UPDATE-CRON-B]）

2. **tools.profile = messaging 導致工具消失**
   - 問題：設定 `tools.profile = messaging` 時，訊息工具外的功能受限，James 困惑「工具不見了」
   - 解法：改成 `tools.profile = full`，然後 `openclaw gateway restart`
   - 來源：2026-03-03-gateway-restart-sop.md

3. **ingest_local.py 改用 plugin CLI 避開全域套件環境**
   - 問題：全域 pip 環境可能缺少必要套件
   - 解法：改走 `memory-lancedb-pro` plugin CLI
   - 來源：decisions.v2.md（[D-2026-03-23-INGEST-LOCAL-PLUGIN-CLI]）

4. **memory-pro upgrade 遇 LLM null 時用 --no-llm 繞過**
   - 問題：升級時若 LLM enrichment 失敗，整個升級會卡住
   - 解法：`--no-llm` 參數繞過 LLM 處理
   - 來源：decisions.v2.md（[D-2026-03-23-MEMORY-PRO-UPGRADE-NO-LLM]）
