# Decisions v2 (Structured SSOT)

> 本檔為結構化 SSOT：每條目必須是 `## [ID] Title` + 第一個 fenced ` ```yaml ` metadata block。
> YAML 解析錯誤或缺必填欄位 → 同步/驗證 hard fail。
>
> Legacy 決策請見：`memory/decisions.md`（逐步遷移）。

---

<a id="D-2026-02-25-DAILY-UPDATE-CRON-B"></a>
## [D-2026-02-25-DAILY-UPDATE-CRON-B] OpenClaw 每日更新 cron 採 B 方案（拆成兩個 job）

```yaml
type: decision
status: active
confidence: high
created_at: 2026-02-25
last_verified_at: 2026-02-25

scope:
  mode: and
  match:
    - global: true

topic_key: openclaw.daily_update_cron_scheme

tags: [openclaw, cron, update, gateway, verify, notification]

cron_scheme: B
jobs:
  - daily-auto-update-openclaw-noon
  - daily-auto-update-openclaw-noon-verify

notify_target: channel:telegram
notify_channel_id: -5222553621
notify_policy: update-related-only
notify_private_dm: false

precedence: 0
supersedes: []
```

### Decision
每日更新採「B 方案」：拆成兩個 cron job，避免更新後重啟 Gateway 導致通知被切斷/漏送。

- Job 1（12:00）只做 update + `openclaw gateway restart`，不負責回報（固定 NO_REPLY）
- Job 2（12:02）做重啟後驗證（版本 + gateway status/RPC probe），並把結果 announce 到監控群

### Rationale
重啟 Gateway 有機會造成通知鏈路短暫中斷；把「動作」與「驗證/通知」拆開，能提高回報可靠性並降低「CLI 回報失敗但其實已重啟」的誤判。

### Operational Notes (non-normative)
- Job 1：update + restart（不發通知）
- Job 2：verify（可包含）
  - `openclaw --version`
  - `openclaw gateway status`（以 RPC probe ok 為主）
  - （可選）`pnpm view openclaw version`
- 所有 update/verify 類結果通知固定送 Telegram 監控群 `chat_id=-5222553621`，避免送私訊（DM）

---

<a id="D-2026-02-25-TELEGRAM-FILE-LIMIT"></a>
## [D-2026-02-25-TELEGRAM-FILE-LIMIT] Telegram 檔案大小限制（Bot API 20MB）

```yaml
type: decision
status: active
confidence: high
created_at: 2026-02-25
last_verified_at: 2026-02-25

scope:
  mode: and
  match:
    - global: true

topic_key: telegram.file_limit

tags: [telegram, file, limit, bot-api]

file_limit_mb: 20
precedence: 0
supersedes: []
```

### Decision
Telegram Bot API 有硬性檔案大小上限 20 MB（`mediaMaxMb` 調大也無用）。

### Operational Notes
若需傳更大的檔案：改用雲端分享連結，或用 PowerShell 下載。

---

<a id="P-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM"></a>
## [P-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM] Gateway restart 高風險：必先通知家豪並等確認

```yaml
type: policy
status: active
confidence: high
created_at: 2026-02-25
last_verified_at: 2026-02-25

scope:
  mode: and
  match:
    - global: true

topic_key: openclaw.gateway_restart_policy

tags: [openclaw, gateway, restart, safety]

requires_human_confirmation: true
required_warning: "重啟後 agent 會暫時離線"
precedence: 0
supersedes: []
```

### Policy
任何會導致 OpenClaw Gateway restart 的操作，都必須：
1) 先通知家豪
2) 清楚告知「重啟後 agent 會暫時離線」
3) 等家豪確認後才可執行

（此為高風險安全規則，禁止默默重啟。）


---

<a id="D-2026-03-23-UPDATE-MECHANISM"></a>
## [D-2026-03-23-UPDATE-MECHANISM] OpenClaw 更新統一採 npm，維持 cron B 方案

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: openclaw.update_mechanism

tags: [openclaw, update, npm, cron, gateway]

cron_scheme: B
jobs:
  - daily-auto-update-openclaw-noon
  - daily-auto-update-openclaw-noon-verify

notify_target: channel:telegram
notify_channel_id: -5222553621
notify_policy: update-related-only
notify_private_dm: false

precedence: 0
supersedes: []
```

### Decision
- 更新指令：`npm install -g openclaw@latest`（統一 npm，不使用 `openclaw update`，該指令僅適用 git source 開發模式）
- 不使用 `openclaw update`：該指令只適用 git source 安裝（開發模式）
- 結論：維持現有 cron B 方案（更新指令統一 npm，避免 pnpm global 造成路徑/驗證問題）

### Rationale
pnpm global 安裝路徑不一致，移除後 restart 會失效；統一 npm 可確保 `C:\Users\admin\AppData\Roaming\npm\openclaw.cmd` 永久可解析。

---

<a id="D-2026-03-23-GATEWAY-RESTART-FIX"></a>
## [D-2026-03-23-GATEWAY-RESTART-FIX] Gateway 服務重啟連不上：統一 npm 安裝路徑

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: openclaw.gateway_restart_fix

tags: [openclaw, gateway, windows, npm, restart]

required_action:
  - npm_install: "npm install -g openclaw@latest"
  - gateway_cmd: "C:/Users/admin/AppData/Roaming/npm/openclaw.cmd"
  - remove_env_override: true

deprecated_alternatives:
  - pnpm_shim: "曾用 pnpm shim 綁定 gateway.cmd，移除 pnpm 後 restart 失效"

precedence: 0
supersedes: [D-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM]
```

### Decision
Windows Gateway 服務重啟後 RPC probe failed / token mismatch 的根因是 Scheduled Task 指向錯誤來源的 openclaw。修法三步：
1. 確保 `openclaw` 由 `npm install -g openclaw@latest` 安裝
2. `~\.openclaw\gateway.cmd` 固定呼叫 `C:\Users\admin\AppData\Roaming\npm\openclaw.cmd`
3. 移除 `OPENCLAW_GATEWAY_TOKEN` 環境變數覆蓋（以 openclaw.json 為準）

### Rationale
`gateway.cmd` 綁 pnpm shim 時，移除 pnpm 後 restart 失效；統一 npm 可避免版本不一致導致 config schema 不相容。

---

<a id="D-2026-03-23-CODEX-OAUTH-PROFILES"></a>
## [D-2026-03-23-CODEX-OAUTH-PROFILES] Codex OAuth profile 補救：token 複製而非重新登入

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: openclaw.codex_oauth_profiles

tags: [openclaw, codex, oauth, auth-profiles, windows]

problem: "openclaw onboard 重新登入只會寫入 default profile，無法指定 active/plus/third"

workaround:
  - step: "把 default profile 的 token 複製到目標 profile"
  - optional: "重置 usageStats.errorCount=0"
  - auth_file: "~\\.openclaw\\agents\\main\\agent\\auth-profiles.json"

precedence: 0
supersedes: []
```

### Decision
`openclaw onboard` 重新登入**只會寫入 `default` profile**，無法指定 `active/plus/third`。補救方式：把 `default` 的 token 複製到目標 profile（必要時重置 `usageStats.errorCount=0`）。

### Rationale
無法透過 CLI 指定 profile 時，手動複製 token 是唯一可靠解法；auth-profiles.json 格式簡單，直接編輯風險低。

---

<a id="D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG"></a>
## [D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG] memory-lancedb-pro 設定三坑：絕對路徑 / apiKey / JSON 轉義

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: memory.lancedb_pro_config

tags: [memory-lancedb-pro, plugin, config, windows, json]

known_issues:
  - plugins_load_paths: "要用絕對路徑，相對路徑會找不到 plugin"
  - embedding_api_key: "仍需非空值，可填 dummy"
  - json_escape: "Windows/PowerShell 寫 JSON 注意反斜線雙重轉義"

precedence: 0
supersedes: []
```

### Decision
memory-lancedb-pro 設定三個常見坑：
1. `plugins.load.paths` 要用絕對路徑
2. `embedding.apiKey` 仍需非空（可填 dummy）
3. Windows/PowerShell 寫 JSON 注意反斜線雙重轉義

---

<a id="D-2026-03-23-INGEST-LOCAL-PLUGIN-CLI"></a>
## [D-2026-03-23-INGEST-LOCAL-PLUGIN-CLI] ingest_local.py 改用 memory-lancedb-pro plugin CLI（避開全域套件環境）

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: openclaw.ingest_local_plugin_cli

tags: [openclaw, ingest, memory-lancedb-pro, cron, windows]

problem: "cron 環境缺少 lancedb 套件，導致 ingest_local.py 直接 import 失敗"

solution:
  - method: "改用 memory-lancedb-pro plugin CLI"
  - command: "openclaw.cmd 完整路徑"
  - import_format: "{memories: [...]}"

use_case: "定時排程（避免依賴全域套件環境）"

precedence: 0
supersedes: []
```

### Decision
cron 環境缺少 lancedb 套件時，改用 memory-lancedb-pro plugin CLI 方式。指令：`openclaw.cmd` 完整路徑 + import 格式需為 `{memories: [...]}`。

---

<a id="D-2026-03-23-BATCH-ERROR-HANDLING"></a>
## [D-2026-03-23-BATCH-ERROR-HANDLING] ingest_local.py 批次處理與錯誤處理原則

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: openclaw.ingest_batch_error_handling

tags: [openclaw, ingest, batch, error-handling, lancedb]

batch_size: 20
cli_timeout_seconds: 300
hash_cache_update: "只在成功後寫回，避免失敗檔案被標成已處理"

ollama_instability:
  - step1: "先手動測 ollama list 確認模型在"
  - step2: "加 --continue-on-error 參數慢慢跑"
  - step3: "避開凌晨 Server 負載高峰期"

failure_handling: "儲存已成功的、跳出迴圈，避免連續失敗浪費資源"

precedence: 0
supersedes: []
```

### Decision
- 批次大小 20 是安全的：單批太大容易 timeout，太小則浪費 CLI 呼叫成本
- CLI timeout 300s per batch
- 失敗時果斷停止：儲存已成功的、跳出迴圈，避免連續失敗浪費資源
- Hash cache 只在成功後寫回：避免失敗檔案被標成已處理
- 懷疑 Ollama 不穩定時：先手動測 `ollama list` 確認模型在 / 加 `--continue-on-error` / 避開凌晨高峰期

---

<a id="D-2026-03-23-MEMORY-PRO-UPGRADE-NO-LLM"></a>
## [D-2026-03-23-MEMORY-PRO-UPGRADE-NO-LLM] memory-pro upgrade 遇到 LLM null 時用 --no-llm 繞過

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: memory.memory_pro_upgrade_no_llm

tags: [memory-lancedb-pro, upgrade, llm, cli]

problem: "openclaw memory-pro upgrade 在 LLM enrichment 階段出現 LLM returned null"

solution: "改用 openclaw memory-pro upgrade --no-llm（繞過 LLM enrichment）"

verified_result: "156 upgraded + 401 already new + 0 errors"

precedence: 0
supersedes: []
```

### Decision
`openclaw memory-pro upgrade` 在 LLM enrichment 階段出現 `LLM returned null` 時，改用 `openclaw memory-pro upgrade --no-llm` 繞過 LLM enrichment。已實測 156 upgraded + 401 already new + 0 errors。

---

<a id="D-2026-03-23-CLI-TIMEOUT-300S"></a>
## [D-2026-03-23-CLI-TIMEOUT-300S] CLI timeout 300s per batch 是安全阈值

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: openclaw.cli_timeout_batch

tags: [openclaw, cli, timeout, batch, performance]

batch_size: 20
cli_timeout_seconds: 300

rationale:
  large_batch: "單批太大容易 timeout"
  small_batch: "太小則浪費 CLI 呼叫成本"

precedence: 0
supersedes: []
```

### Decision
CLI timeout 300s per batch；批次大小 20 是安全阈值（太大易 timeout，太小則浪費成本）。

---

<a id="D-2026-03-23-TELEGRAM-GROUP-COMMAND"></a>
## [D-2026-03-23-TELEGRAM-GROUP-COMMAND] Telegram 群組 /new 失敗：需設定 allowFrom / groupAllowFrom

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - channel: telegram
    - global: true

topic_key: telegram.group_command_allow

tags: [telegram, auth, command, group, openclaw]

problem: "在群組送出 /new 回覆 You are not authorized，但私訊可用"

root_cause: "群組指令授權吃 Telegram channel allowlist，非 tools.elevated.allowFrom"

solution:
  - channels_telegram_allowFrom: '["7790964999"]'
  - channels_telegram_groupAllowFrom: '["7790964999"]'
  - require_restart: true

precedence: 0
supersedes: []
```

### Decision
Telegram 群組無法使用 `/new` 的根因是群組指令授權實際吃 Telegram channel 的 allowlist（不是 `tools.elevated.allowFrom`）。修法：在 `openclaw.json` 加上 `channels.telegram.allowFrom: ["7790964999"]` + `groupAllowFrom: ["7790964999"]`，然後 `openclaw gateway restart`。

---

<a id="D-2026-03-23-PRECISE-READ-STRATEGY"></a>
## [D-2026-03-23-PRECISE-READ-STRATEGY] 精準讀檔策略：先定位再小範圍讀

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: agent.precise_read_strategy

tags: [agent, read, strategy, token, efficiency]

steps:
  - step1: "Select-String 拿行號"
  - step2: "小範圍 read（+-20 行）"
  - step3: "每次小改 20-50 行"

avoid: "避免重複讀大檔；對話 > 80k tokens 主動建議 /reset"

enoent_handling:
  - step1: "先查 LanceDB / memory 決策"
  - step2: "若需原文再查 QMD"
  - step3: "只有記憶層無結論時才可進入程式碼搜尋"
  - step4: "搜尋前先縮到單一目標（函式名/檔名/模組名）"
  - forbidden: "禁止對 dist/、node_modules/、整個 workspace 做多輪全文暴掃"

precedence: 0
supersedes: []
```

### Decision
- 精準定位：`Select-String` 拿行號 -> 小範圍 read（+-20 行）-> 每次小改 20-50 行
- 避免重複讀大檔：用 offset/limit
- 對話 > 80k tokens 主動建議 `/reset`
- ENOENT 偵錯：先查 LanceDB / memory 決策；若需原文再查 QMD；只有記憶層無結論時才進入程式碼搜尋；禁止對 `dist/`、`node_modules/`、整個 workspace 做多輪全文暴掃

---

<a id="D-2026-03-23-QMD-LANCEDB-DIVISION"></a>
## [D-2026-03-23-QMD-LANCEDB-DIVISION] QMD 與 LanceDB 分工：QMD 負責索引，Lancedb 負責結論

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: agent.qmd_lancedb_division

tags: [qmd, lancedb, memory, search, index]

division:
  qmd: "負責檔案索引與原文取片段（qmd query/search -> qmd get/multi-get）"
  lancedb: "負責存精煉結論/偏好/決策並用 recall 快速取回"

memorySearch_setting: "sources = [memory]（不索引 sessions）"

rationale:
  - avoid_pollution: "sessions 內含大量嘗試/雜訊；長期記憶以 B 主動複盤->精煉結論->寫回為準"
  - performance: "排除 sessions 可大幅縮短 daily index 時間、降低 CPU/IO 負擔"
  - stability: "避開長文本/大檔導致 embedding 失敗或卡住的風險"

precedence: 0
supersedes: []
```

### Decision
- **QMD**：負責檔案索引與原文取片段（`qmd query/search` -> `qmd get/multi-get`）
- **LanceDB**：負責存「精煉結論/偏好/決策」並用 recall 快速取回
- **memorySearch**：維持 `sources = ["memory"]`（不索引 sessions）
- QMD 的 daily index / embed 完成，不代表 OpenClaw 的 memory index 已完成；兩者是獨立系統

---

<a id="D-2026-03-23-OPENCODE-ABANDONED"></a>
## [D-2026-03-23-OPENCODE-ABANDONED] 放棄 OpenCode TUI，改用 exec + MiniMax

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: agent.opencode_abandoned

tags: [opencode, coding, agent, minimax, exec]

abandoned_tool: OpenCode TUI

reason: "OpenCode 等待完整回覆才能顯示（streaming 差異）；MiniMax API 本身較慢，疊加後更慢"

current_approach: "exec + MiniMax 直接處理 coding 任務"

precedence: 0
supersedes: []
```

### Decision
放棄 OpenCode TUI，改用 `exec + MiniMax` 直接處理 coding 任務。原因：OpenCode 等待完整回覆才能顯示（streaming 差異）；MiniMax API 本身較慢，疊加後更慢。

---

<a id="D-2026-03-23-AUTO-EXPERIENCE-LOOP"></a>
## [D-2026-03-23-AUTO-EXPERIENCE-LOOP] 主動模式 B：家豪確認後主動詢問是否記錄經驗

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: agent.auto_experience_loop

tags: [experience, memory, recall, loop, upsert]

trigger: "家豪確認問題已解決（OK/讚/好了/成功）"

required_action: "Claw 必須主動詢問：這次的解法要不要記成一條可復用的經驗？"

writeback_format:
  - 觸發條件
  - 正確作法（指令/設定）
  - 禁忌/坑
  - 版本/環境（Windows/WSL/Discord 等）

writeback_rules:
  - only_refined: "只寫精煉結論；原文/長文用 QMD 取片段"
  - why_field: "why/根因欄只寫已驗證事實；未驗證假設標記 [unverified] 或不寫"
  - recall_first: "寫入前先透過 memory_recall 做相似記憶搜尋"

upsert_policy:
  found_similar: "主動詢問家豪：更新舊的還是保留兩條並標註版本差異？"
  not_found: "直接建立新記憶（memory_store）"

precedence: 0
supersedes: []
```

### Decision
只要家豪確認問題已解決，Claw **必須主動詢問**：「這次的解法要不要記成一條可復用的經驗？」只有在家豪同意後，才將經驗寫入長期記憶。寫入格式：觸發條件 / 正確作法 / 禁忌坑 / 版本環境。只寫精煉結論；原文用 QMD 取片段；why/根因欄只寫已驗證事實。

---

<a id="D-2026-03-23-GITHUB-REACTIVE-SEARCH"></a>
## [D-2026-03-23-GITHUB-REACTIVE-SEARCH] GitHub 查閱節奏：Release 前必看、每週掃一次、出事才查 Closed

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-23
last_verified_at: 2026-03-23

scope:
  mode: and
  match:
    - global: true

topic_key: agent.github_search_rhythm

tags: [github, search, openclaw, issue, bug, workflow]

release_based:
  trigger: "準備升級 OpenClaw 之前"
  action: "先看 GitHub Releases / changelog"
  purpose: "確認是否有 Breaking Changes / config schema 變動"

weekly_catchup:
  action: "GitHub Issues -> Sort: Newest，只掃標題，不深讀"
  purpose: "提早知道重大坑（memory leak、Windows 崩潰、相容性問題）"
  frequency: "每週一次，5 分鐘"

reactive_search:
  trigger: "出事才查（Timeout、socket、path/權限、平台差異）或討論進階配置"
  query: "is:issue is:closed <錯誤訊息或關鍵字>"
  priority: "bug / discussion 類型、有 workaround 的 Closed 案"

knowledge回流: "找到有效 workaround 並驗證成功後，納入 Auto-Experience Loop"

precedence: 0
supersedes: []
```

### Decision
GitHub 查閱三種節奏：
1. **Release-based**：升級前必看 changelog，確認 Breaking Changes
2. **Weekly catch-up**：每週掃一次 newest，只看標題不深讀
3. **Reactive search**：出事才查，優先搜 Closed issues + bug/discussion 類型 + 有 workaround 的案子



---

<a id="D-2026-03-19-MEMORY-PRO-UPGRADE-NO-LLM"></a>
## [D-2026-03-19-MEMORY-PRO-UPGRADE-NO-LLM] memory-pro upgrade 遇 LLM enrichment 失敗時改用 `--no-llm`

```yaml
type: decision
status: active
confidence: high
created_at: 2026-03-19
last_verified_at: 2026-03-19

scope:
  mode: and
  match:
    - global: true

topic_key: memory_pro.upgrade_no_llm_fallback

tags: [memory-pro, upgrade, llm, fallback, lancedb]

precedence: 0
supersedes: []
```

### Decision
當 `openclaw memory-pro upgrade` 在 LLM enrichment 階段出現 `LLM returned null` 時，改用：

`openclaw memory-pro upgrade --no-llm`

直接略過 LLM enrichment，先完成記憶格式升級。

### Rationale
升級流程的目標是先完成資料結構遷移；若 enrichment 不穩，讓整體 upgrade 卡住的代價更高。`--no-llm` 是可接受的穩定 fallback。

### Verification
- 已驗證結果：`156 upgraded + 401 already new + 0 errors`

---

<a id="P-2026-03-16-CLI-TIMEOUT-BATCH-POLICY"></a>
## [P-2026-03-16-CLI-TIMEOUT-BATCH-POLICY] CLI 批次處理統一採 20 筆 / 300 秒 / 成功後寫 cache

```yaml
type: policy
status: active
confidence: high
created_at: 2026-03-16
last_verified_at: 2026-03-16

scope:
  mode: and
  match:
    - global: true

topic_key: cli.batch_timeout_policy

tags: [cli, batch, timeout, cache, reliability]

batch_size: 20
timeout_seconds: 300
write_cache_on_success_only: true
stop_on_batch_failure: true

precedence: 0
supersedes: []
```

### Policy
批量 CLI 任務統一採以下原則：
1. 批次大小 20
2. 每批 timeout 300 秒
3. 只有成功後才寫回 hash/cache
4. 若單批失敗，先停止後續批次，不連續盲跑

### Rationale
批次太大容易 timeout；太小又浪費 CLI 呼叫成本。20/300s 是實測穩定折衷。

---

<a id="P-2026-03-21-SUBAGENT-STRATEGY"></a>
## [P-2026-03-21-SUBAGENT-STRATEGY] Sub-Agent 策略：>5 分鐘 / >3 件批量 / >80k context 優先拆開

```yaml
type: policy
status: active
confidence: high
created_at: 2026-03-21
last_verified_at: 2026-03-21

scope:
  mode: and
  match:
    - global: true

topic_key: subagent.strategy

tags: [subagent, routing, timeout, context, parallelism]

hard_limit: 6
default_model: minimax-portal/MiniMax-M2.7
default_timeout_seconds: 600
fallback_chain:
  - openai-codex/gpt-5.4-mini
  - openai-codex/gpt-5.3-codex

precedence: 0
supersedes: []
```

### Policy
Sub-agent 使用策略：
- 預估任務 > 5 分鐘 → 優先拆開
- 批量任務 > 3 件 → 優先拆開
- context > 80k tokens → 優先拆開
- 主線只做收斂 / 判斷 / 下指令 / 寫入 / 回報
- sub-agent 正在跑時，不再隨意追加新任務

### Rationale
避免主線 context 污染、降低 timeout 風險、提高大任務完成率。

---

<a id="P-2026-02-15-PRECISE-READING-WINDOW"></a>
## [P-2026-02-15-PRECISE-READING-WINDOW] 精準讀檔策略：先定位，再小窗 read

```yaml
type: policy
status: active
confidence: high
created_at: 2026-02-15
last_verified_at: 2026-02-15

scope:
  mode: and
  match:
    - global: true

topic_key: code_reading.precise_windowing

tags: [read, tokens, search, efficiency, verification]

precedence: 0
supersedes: []
```

### Policy
讀大檔時採用：
1. 先用搜尋定位目標行號
2. 再用小範圍 read（通常 ±20 行）
3. 每次小改 20–50 行
4. 對話 > 80k tokens 時主動考慮 `/reset`

### Rationale
避免重複讀大檔、降低 token 浪費、提高首次命中率。

---

<a id="P-2026-03-09-PATH-DEBUG-RECALL-FIRST"></a>
## [P-2026-03-09-PATH-DEBUG-RECALL-FIRST] ENOENT / 路徑解析錯誤：先 recall，再縮到單一目標驗證

```yaml
type: policy
status: active
confidence: high
created_at: 2026-03-09
last_verified_at: 2026-03-09

scope:
  mode: and
  match:
    - global: true

topic_key: path_debug.recall_then_verify

tags: [path, enoent, debug, recall, verify]

precedence: 0
supersedes: []
```

### Policy
遇到 `ENOENT`、tilde 展開、路徑拼接、重複前綴等路徑解析錯誤時：
1. 先查 LanceDB / memory 決策
2. 若需原文，再查 QMD
3. 只有記憶層沒有結論時，才進入程式碼搜尋
4. 程式碼搜尋必須先縮到單一目標，再小範圍 read
5. 禁止一上來暴掃整個 `dist/` / `node_modules/` / workspace

### Rationale
避免把可回收的既有經驗，變成高成本的主線探索。

---

<a id="D-2026-02-28-QMD-LANCEDB-ROLE-SPLIT"></a>
## [D-2026-02-28-QMD-LANCEDB-ROLE-SPLIT] QMD 與 LanceDB 分工：QMD 查原文，LanceDB 存精煉結論

```yaml
type: decision
status: active
confidence: high
created_at: 2026-02-28
last_verified_at: 2026-02-28

scope:
  mode: and
  match:
    - global: true

topic_key: memory.qmd_vs_lancedb_roles

tags: [qmd, lancedb, memory, search, ssot]

precedence: 0
supersedes: []
```

### Decision
- **QMD**：負責檔案索引與原文片段查詢（`search/query → get`）
- **LanceDB / memory-lancedb-pro**：負責存精煉結論、偏好、決策，用 recall 快速取回

### Rationale
兩者是不同系統；QMD 的 index 完成，不代表 OpenClaw 的 memory index 完成。

---

<a id="D-2026-02-28-MEMORY-SEARCH-MEMORY-ONLY"></a>
## [D-2026-02-28-MEMORY-SEARCH-MEMORY-ONLY] Memory Search 維持 memory-only，不索引 sessions

```yaml
type: decision
status: active
confidence: high
created_at: 2026-02-28
last_verified_at: 2026-02-28

scope:
  mode: and
  match:
    - global: true

topic_key: memory_search.memory_only

tags: [memory-search, sessions, noise, indexing]

sources:
  - memory
exclude_sources:
  - sessions

precedence: 0
supersedes: []
```

### Decision
維持 `agents.defaults.memorySearch.sources = ["memory"]`，不回退到 `sessions`。

### Rationale
- 避免 sessions 污染（大量嘗試/雜訊）
- 縮短 daily index 時間
- 降低長文本 embedding 失敗風險
- 查舊對話原文時改走 QMD，而不是 memorySearch.sessions

---

<a id="P-2026-02-28-MEMORY-UPSERT-DEPRECATE-RULES"></a>
## [P-2026-02-28-MEMORY-UPSERT-DEPRECATE-RULES] 記憶寫入採 upsert、Deprecated 軟刪除、版本欄位必填

```yaml
type: policy
status: active
confidence: high
created_at: 2026-02-28
last_verified_at: 2026-02-28

scope:
  mode: and
  match:
    - global: true

topic_key: memory.upsert_and_deprecate_rules

tags: [memory, upsert, deprecated, versioning, governance]

precedence: 0
supersedes: []
```

### Policy
記憶治理採以下規則：
1. 寫入前先做相似記憶搜尋
2. 找到高度相似舊記憶時，預設走 update / upsert
3. 舊結論失效時，不直接硬刪；先標 `[Deprecated]` 並標示被哪條新結論取代
4. 任何版本高度相關的經驗，寫回時必填版本 / 環境欄位


---

## [D-2026-03-31-PR426-IMPORT-MARKDOWN] PR #426 import-markdown 實作改善已套用到本地 Extension

```yaml
type: decision
status: active
confidence: confirmed
created_at: 2026-03-31
last_verified_at: 2026-03-31

scope:
  mode: and
  match:
    - machine: 客廳電腦-家豪
    - global: true

topic_key: memory.import_markdown_cli

tags: [memory-lancedb-pro, pr-426, import-markdown, local-deploy]

problem: "PR #426 的 import-markdown CLI 功能改善（--dedup、BOM/CRLF修復、bullet格式擴展）需要套用到本地 OpenClaw Extension 才能實際使用"

solution:
  - "已將 PR #426 分支（feat/import-markdown-cli）的 cli.ts 複製到本地 Extension 路徑"
  - "實際加載路徑：C:\Users\admin\.openclaw\extensions\memory-lancedb-pro\cli.ts"
  - "備份檔案：C:\Users\admin\.openclaw\extensions\memory-lancedb-pro\cli.ts.bak_20260331_212943"
  - "PR 分支已推送至 jlin53882/memory-lancedb-pro 的 feat/import-markdown-cli"

details:
  cli_size_bytes: 55497
  old_cli_size_bytes: 52388
  new_options: ["--dedup", "--min-text-length", "--importance"]
  fixes: ["UTF-8 BOM 移除", "CRLF 正規化", "Bullet 格式擴展（-/*/+）"]

notes:
  - "Extension 無 git，是從 plugins/memory-lancedb-pro-pr 複製過去的"
  - "plugins/memory-lancedb-pro-pr 是 PR #426 的本地 clone（feat/import-markdown-cli 分支）"
  - "Gateway 重啟後生效"

references:
  - "PR #426: https://github.com/CortexReach/memory-lancedb-pro/pull/426"
  - "Issue #344: https://github.com/CortexReach/memory-lancedb-pro/issues/344"
  - "Analysis: C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test\PR426-ANALYSIS.md"
```

