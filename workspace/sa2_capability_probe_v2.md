# SA-2 CapabilityProbe v2 — 工具能力盤點報告

**執行時間：** 2026-03-22 13:14 GMT+8
**目標：** 盤點 OpenClaw 當前可用工具，識別缺口

---

## 1. 現有工具清單（Current Tools）

### 核心工具（系統級，來自 Tool Schema）

| 工具名 | 說明 | 狀態 |
|--------|------|------|
| `read` | 讀取檔案（文字/圖片），支援 offset/limit | ✅ 可用 |
| `write` | 建立或覆寫檔案（自動 UTF-8） | ✅ 可用 |
| `edit` | 精準文字取代編輯 | ✅ 可用 |
| `exec` | 執行 Shell 命令（支援 PTY/yieldMs/background） | ✅ 可用 |
| `process` | 管理背景 exec sessions | ✅ 可用 |
| `web_search` | Brave Search API 網頁搜尋 | ✅ 可用 |
| `web_fetch` | 擷取 URL 轉 markdown/text | ✅ 可用 |
| `browser` | OpenClaw 瀏覽器控制（profiles: user/chrome-relay/openclaw） | ✅ 可用 |
| `canvas` | 控制 Node Canvas（present/snapshot/eval） | ✅ 可用 |
| `message` | 跨 channel 發送訊息（Discord/Telegram） | ✅ 可用 |
| `image` | AI 視覺模型分析圖片 | ✅ 可用 |
| `tts` | 文字轉語音 | ✅ 可用 |
| `pdf` / `pdfs` | PDF 分析（支援原生/OCR fallback） | ✅ 可用 |
| `memory_recall` | LanceDB 向量搜尋 | ✅ 可用 |
| `memory_store` | 寫入長期記憶 | ✅ 可用 |
| `memory_update` | 更新記憶內容 | ✅ 可用 |
| `memory_forget` | 刪除指定記憶 | ✅ 可用 |
| `memory_list` | 列出近期記憶 | ✅ 可用 |
| `memory_stats` | 記憶使用統計 | ✅ 可用 |
| `sessions_yield` | 終止當前 turn 並等待 sub-agent 結果 | ✅ 可用 |

### Workspace 自建工具（`workspace/tools/`）

| 工具路徑 | 說明 | 狀態 |
|----------|------|------|
| `tools/file/escape_md_to_html.py` | Markdown 轉 HTML | ⚠️ 未通过标准化入口调用 |
| `tools/file/extract_docx_text.py` | DOCX 文字萃取 | ⚠️ 未通过标准化入口调用 |
| `tools/file/scan_translations.py` | 翻譯檔案掃描 | ⚠️ 未通过标准化入口调用 |
| `tools/pdf/convert_md_to_pdf.py` | Markdown 轉 PDF | ⚠️ 未通过标准化入口调用 |
| `tools/pdf/extract_pdf_text.py` | PDF 文字萃取 | ⚠️ 未通过标准化入口调用 |
| `tools/pdf/pdf_to_images.py` | PDF 轉圖片 | ⚠️ 未通过标准化入口调用 |
| `tools/pdf/search_pdf.py` | PDF 關鍵字搜尋 | ⚠️ 未通过标准化入口调用 |
| `tools/utils/batch_exec_analyze.py` | 批次 exec 分析 | ⚠️ 未通过标准化入口调用 |
| `tools/utils/make_month_vocab.py` | 月詞彙表生成 | ⚠️ 未通过标准化入口调用 |
| `tools/utils/search_text.py` | 文字搜尋工具 | ⚠️ 未通过标准化入口调用 |

### Skills（`openclaw/skills/` + `workspace/skills/`）

| 技能 | 用途 |
|------|------|
| `clawhub` | 安裝/發布 agent skills |
| `coding-agent` | 委派 Codex/Claude Code 編碼任務 |
| `discord` | Discord 操作 |
| `gh-issues` | GitHub issues 追蹤與 PR |
| `github` | GitHub CLI 操作 |
| `healthcheck` | 主機安全強化 |
| `node-connect` | 節點連線診斷 |
| `session-logs` | 對話日誌分析 |
| `skill-creator` | 建立/改善 AgentSkills |
| `summarize` | URL/檔案/YouTube 摘要 |
| `weather` | 天氣查詢 |
| `agent-browser` | Rust 無頭瀏覽器自動化 |
| `agent-self-review` | Agent 自我檢討 |
| `agentlens` | 程式碼庫階層導覽 |
| `batch-processor` | 批量文件處理 |
| `code-review` | 系統化程式碼審查 |
| `codex-quota` | Codex 配額查詢 |
| `find-skills` | 技能發現與安裝 |
| `memory-compress` | 記憶壓縮（80k+ tokens 觸發） |
| `opencode-controller` | Opencode 控制 |
| `parallel-processing-patterns` | 並行處理模式 |
| `proactive-agent` | 主動式 Agent 模式 |
| `qmd` | QMD 本地知識庫搜尋 |
| `self-improvement` | 持續學習 |
| `skill-vetting` | ClawHub 技能審查 |

---

## 2. 缺口分析（Gap Analysis）

| 任務類型 | 缺口描述 | 優先級 |
|----------|----------|--------|
| 批次檔案處理 | 自建 tools 無法通过统一入口调用，需手動 exec python | **HIGH** |
| 視覺化呈現 | 無專用 chart/diagram 生成工具，須依賴程式碼或外部 API | **HIGH** |
| Linear 整合 | 無 Linear API 工具，無法讀寫 Linear issues | **MED** |
| 資料庫操作 | 無直接 DB 查詢工具（PostgreSQL/SQLite） | **MED** |
| 行事曆整合 | 無 Google Calendar / Outlook API 整合 | **MED** |
| 正式檔案轉檔 | 自建 docx/xlsx/odt 工具缺失，僅 docx 有基礎萃取 | **MED** |
| 自動化測試報告 | 無 JUnit/TestNG 等格式解析工具 | **LOW** |
| Git 圖形化 | 無 git log --graph 等視覺化輸出 | **LOW** |
| Container 管理 | 無 Docker/容器狀態查詢工具 | **LOW** |

---

## 3. 未充分利用的工具（Underused Tools）

| 工具 | 說明 |
|------|------|
| `batch-processor` skill | 批量文件處理，但幾乎未啟用 |
| `parallel-processing-patterns` skill | 並行處理模式文件，無實際調用 |
| `agent-browser` skill | Rust 無頭瀏覽器自動化，穩定性待驗證 |
| `codex-quota` skill | Codex 配額查詢，幾乎未用 |
| `canvas` | 可用於渲染/快照，但很少使用 |
| `tts` | 文字轉語音，幾乎未使用 |

---

## 4. 建議新工具（Recommended New Tools）

| 建議工具 | 類別 | 理由 |
|----------|------|------|
| `tools/batch/batch_file_processor.py` | file | 統一入口封裝 workspace/tools 所有批次工具 |
| `tools/office/extract_xlsx.py` | file | Excel 讀取支援（目前缺口） |
| `tools/office/extract_odt.py` | file | ODT 格式支援 |
| `tools/viz/generate_chart.py` | utils | 從數據生成 chart（bar/line/pie） |
| `Linear API wrapper` | — | 考慮透過 exec + curl 或獨立 skill |

---

## 5. 工具覆蓋分數（Tool Coverage Score）

```json
{
  "current_tools": [
    "read: 讀取檔案內容（支援 offset/limit）",
    "write: 建立或覆寫檔案（自動 UTF-8）",
    "edit: 精準文字取代編輯",
    "exec: 執行 Shell 命令（PTY/yieldMs/background）",
    "process: 管理背景 exec sessions",
    "web_search: Brave Search API 網頁搜尋",
    "web_fetch: URL 擷取轉 markdown/text",
    "browser: OpenClaw 瀏覽器控制",
    "canvas: Node Canvas 控制與快照",
    "message: 跨 channel 訊息發送（Discord/Telegram）",
    "image: AI 視覺模型圖片分析",
    "tts: 文字轉語音",
    "pdf/pdfs: PDF 分析",
    "memory_recall: LanceDB 向量搜尋",
    "memory_store: 寫入長期記憶",
    "memory_update: 更新記憶內容",
    "memory_forget: 刪除指定記憶",
    "memory_list: 列出近期記憶",
    "memory_stats: 記憶使用統計",
    "sessions_yield: 終止 turn 等待 sub-agent 結果",
    "workspace/tools/file/*.py: 自建檔案處理工具（未標準化入口）",
    "workspace/tools/pdf/*.py: 自建 PDF 工具（未標準化入口）",
    "workspace/tools/utils/*.py: 自建通用工具（未標準化入口）"
  ],
  "gap_analysis": [
    {"task_type": "批次檔案統一處理", "missing_tool": "batch_processor 標準化入口", "priority": "HIGH"},
    {"task_type": "視覺化圖表生成", "missing_tool": "chart/diagram 生成工具", "priority": "HIGH"},
    {"task_type": "Linear issue 管理", "missing_tool": "Linear API 整合", "priority": "MED"},
    {"task_type": "關聯式資料庫查詢", "missing_tool": "DB 直接查詢工具", "priority": "MED"},
    {"task_type": "行事曆 API 整合", "missing_tool": "Google/Outlook Calendar", "priority": "MED"},
    {"task_type": "Office 格式轉換", "missing_tool": "xlsx/odt 等格式支援", "priority": "MED"},
    {"task_type": "自動化測試報告解析", "missing_tool": "JUnit/TestNG 解析", "priority": "LOW"},
    {"task_type": "Container 監控", "missing_tool": "Docker 狀態查詢", "priority": "LOW"}
  ],
  "underused_tools": [
    "batch-processor skill: 批量文件處理，几乎未启用",
    "parallel-processing-patterns skill: 并行处理文档，无实际调用",
    "agent-browser skill: Rust 无头浏览器，稳定性待验证",
    "codex-quota skill: Codex 配额查询，几乎未用",
    "canvas: 可用于渲染/快照，但很少使用",
    "tts: 文字转语音，几乎未使用"
  ],
  "recommended_new_tools": [
    "tools/batch/batch_file_processor.py: 统一入口封装所有批次工具",
    "tools/office/extract_xlsx.py: Excel 读取支持",
    "tools/office/extract_odt.py: ODT 格式支持",
    "tools/viz/generate_chart.py: 从数据生成图表"
  ],
  "tool_coverage_score": "72/100"
}
```

**評分說明：**
- 核心工具鏈完整（read/write/edit/exec/browser/message）✅
- 自建 tools 存在但缺乏標準化統一入口 ⚠️
- 企業工具（Linear/DB/Calendar）覆蓋不足 ⚠️
- 視覺化能力缺口明顯 ⚠️

---

*報告產生：SA-2 CapabilityProbe v2 | 2026-03-22*