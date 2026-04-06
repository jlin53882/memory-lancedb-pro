# PR/開發流程 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/

---

## 核心知識點

1. **PR 工作流鐵則（2026-03-20 James 確認）**
   - 內容：接工作前先讀 `docs/AI_WORKFLOW_MANUAL.md` → 先建 feature branch → branch 內完成實作與驗證 → 確認變更都在 branch 上 → 建立 PR。**嚴禁先在 main 完成實作再補 PR**
   - 來源：AGENTS.md [LEARNED_RULES] + 2026-03-18-ai-workflow-guide.md

2. **驗證迴圈（每次輸出 6 步驟）**
   - 內容：Build → Types → Lint → Tests → Security（grep api_key）→ Diff。全部通過才算完成
   - 來源：AGENTS.md 開發工作流章節

3. **AI_WORKFLOW_MANUAL.md 為主工作指南**
   - 內容：含 James 偏好、專案背景（Minecraft/Stock Trading/Workspace）、uv/備份/編碼規則、各專案 SOP
   - 來源：docs/AI_WORKFLOW_MANUAL.md

4. **PR merge 前嚴禁刪除 source branch**
   - 內容：方便回查，任何人不得在 merge 前刪除 source branch
   - 來源：AGENTS.md [LEARNED_RULES]

5. **Sub-agent 完成後必檢查 git status 和完整輸出**
   - 內容：發現「說要做但沒做」的 sub-agent，立即自己補做
   - 來源：AGENTS.md [LEARNED_RULES]

6. **PR review 修正完成後需再跑全測試**
   - 內容：每次 PR review 修正完成後，再跑 `pytest -q` 確認所有單元測試通過
   - 來源：AGENTS.md [LEARNED_RULES]

7. **設計流程優先檢索（強制規則）**
   - 內容：收到「設計、流程、開發、重構」相關問題，**必須先讀 `docs/dev_process_flow.md`**，確認流程後才能輸出答案
   - 來源：AGENTS.md 強制規則章節

8. **Plan-First 觸發條件：任務 >3 步驟**
   - 內容：Plan 階段 → Execute 階段（每 3~5 步回報進度）→ Verify 階段
   - 來源：AGENTS.md 執行工作流章節

9. **GitHub Issue 回報格式（2026-03-23 起強制）**
   - 內容：所有 gh issue create/edit 的 body 必須用 Markdown 語法；正確流程：草稿先寫到 `.md` 檔 → 用 `--body-file` 上傳
   - 來源：AGENTS.md §E

10. **Anti-hallucination SOP 體系（2026-03-08 建立）**
    - 內容：4 份 SOP 文件（routing/query/ops/fileops）；涉及「工具/SOP/流程是否存在」的問題，回覆前必須先做記憶查核並以實檔驗證
    - 來源：2026-03-08-anti-hallucination-sop.md

---

## 常見踩坑

1. **先在 main 完成實作再補 PR**
   - 問題：force push 與歷史汙染，違反 PR 流程紀律
   - 解法：接到 PR 任務當下立刻建立 feature branch，之後所有實作都在 branch 內
   - 來源：AGENTS.md [LEARNED_RULES]

2. **忘記跑 pytest 直接起動**
   - 問題：跳過測試步驟，導致問題未被及時發現（2026-03-19 事件）
   - 解法：修改 → 備份 → `uv run pytest -q` → `uv run main.py`，三步缺一不可
   - 來源：2026-03-19-forgot-pytest-lesson.md

3. **James 報測試失敗時先說本地通過**
   - 問題：應先問「清除 `__pycache__` 了嗎」，而非直接否認
   - 解法：收到失敗回報，第一句問快取問題，同時檢查環境
   - 來源：AGENTS.md [LEARNED_RULES]

4. **批次修改時只改部分模組忘記全測試**
   - 問題：Module verification fix（2026-03-20）需要全部跑完確認 UI 功能正確傳入
   - 解法：大量修改後跑完整驗證，不只測單一模組
   - 來源：2026-03-20-module-verification-fix.md
