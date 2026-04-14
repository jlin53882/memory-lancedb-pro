# Proposal A Phase 1 — 完整整理與執行流程

> 整理日期：2026-04-08
> 用途：James 向 maintainer 確認方向 + 確認後的執行參考

---

## 一、Phase 1 完整內容（所有相關 PR）

### PR #493 — Phase 1（原始版，已關閉）

**分支**：`feat/proposal-a-v3-clean`
**狀態**：✅ AliceLJY `APPROVED` → ❌ rwmjhb `CHANGES_REQUESTED` → 關閉
**commits**：18 個（含完整 Phase 1 + bug fixes）

### PR #507 — Phase 1 v3（re-org 版，已關閉）

**分支**：`feat/proposal-a-v3-clean`（與 #493 同分支，rebase 更新）
**狀態**：❌ rwmjhb 關閉（原因：branch topology 錯誤 + 其他 PR 的問題）
**commits**：與 #493 相同或更完整

### 從 #493 拆出去的獨立 PR（全部 🟡 Open，未合併）

| PR | 標題 | 內容 | 與 Phase 1 的關係 |
|----|------|------|------------------|
| #498 | fix: remove invalid WeakSet.clear() | 移除不存在的 WeakSet.clear() | 原本包在 #493 內 |
| #500 | fix: skip applyRecencyBoost when decayEngine active | 防止 recency 雙重加成 | 原本包在 #493 內 |
| #510 | fix: strip entire wrapper line in stripEnvelopeMetadata | 修復 wrapper 拆除不完整 | 原本包在 #493 內 |

---

## 二、Phase 1 #493 的 18 個 Commits 完整清單

| # | 內容摘要 | 等級 | 說明 |
|---|---------|------|------|
| 1 | pendingRecall Map + agent_end hook + before_prompt_build hook (p5) + session_end hook + isRecallUsed() | Init | Phase 1 核心框架 |
| 2 | pendingRecall responseText 來自前一輪 → before_prompt_build CREATES、agent_end 只 WRITES | P1 | 確保回應與記憶對齊 |
| 3 | parseSmartMetadata 用空 metadata 返回 fallback → 改用 store.getById() | P2 | 讀到真實資料 |
| 4 | patchMetadata 只更新 JSON blob 不更新 row importance → 改用 store.update() | P2 | importance 變更真的影響排名 |
| 5 | pendingRecall.delete() 移到 feedback hook finally block | P2 | 防止重複評分 |
| 6 | confirmed use 重置 bad_recall_count 為 0 | P2 | threshold 只適用連續 miss |
| 7 | retrieveWithTrace 傳遞 source 參數 | P3 | 對齊 debug 與實際行為 |
| 8 | isRecallUsed 新增 direct injected-ID 檢查 | P1 | 對 ID 做 AND 檢查 |
| 9 | rerank env vars 加 rerank-enabled guard | — | 防止未設定時啟動失敗 |
| 10 | multi-line wrapper stripping | P2 | 移除 boilerplate continuation lines |
| 11 | isRecallUsed 檢查 injected summary verbatim match（>=10 chars）| P1 | 對 summary 做 AND 檢查 |
| 12 | confirm/error keywords 從 responseText 改為從 event.messages 取 user prompt | P1 | 對下一輪 user prompt 檢查 |
| 13 | parsePluginConfig 加入 feedback 區塊解析 | P2 | 讓 config 可以設定 feedback |
| 14 | bad_recall_count 在兩處都 increment → 移除 feedback hook 的 increment | P2 | 避免雙重計數 |
| 15 | 每個 recallId 個別評分（summaryMap: recallId → summary）| P1 | 避免集體 boost/penalty |
| 16 | pendingRecall key 改用 sessionKey:agentId 複合鍵 | P2 | 跨 agent 不覆寫 |
| 17 | CJK keywords 從單字改為完整片語（是→是對的、對→確認、錯→錯誤）| P1 | 避免普通對話 false positive |
| 18 | session_end 鉤子未正確清理 → startsWith pattern matching | P3 | 複合鍵也能正確清理 |

**Phase 1 核心實作完整，18 個 commits 全部在分支內，無遺漏。**

---

## 三、⚠️ 目前最大障礙：#498、#500、#510 未合併

這三個 PR 是從 #493 拆出去的，但它們全部還是 Open、未合併。

**問題**：
- 這三個 PR 包含在 #493 的 commit 歷史中
- 如果 Phase 1 (#507 精神) 要 rebase 到 master，會遇到一個問題：
  - 如果 master 沒有這三個 PR → Phase 1 branch 包含這三個 commits（正確）
  - 如果這三個 PR 先 merge → Phase 1 rebase 後會有重複 commits

**選項**：

| 選項 | 做法 | 風險 |
|------|------|------|
| A | 先合併 #498、#500、#510，再 rebase Phase 1 branch 到 master，然後 force push 更新 #507 | 最小 |
| B | 先合併三個 PR，再重新打 Phase 1 PR（drop 三個重複 commits）| 需要重新 commit |
| C | 直接以 Phase 1 branch 重新打 PR，不管 #498/#500/#510 狀態 | 可能被 maintainer 要求先處理 |

---

## 四、rwmjhb 對 #493 的四個反對理由，現在的狀態

| 理由 | 當時問題 | 現狀 |
|------|---------|------|
| 1. Global usage markers 破壞 per-item scoring | "remember"/"as you mentioned" 先返回 true | Commit #11 已修復：加入 injectedSummaries verbatim + injectedID AND check；Commit #17 移除通用片語 |
| 2. Feedback hooks 在 autoCapture 內 | hooks 會隨 autoCapture=false 消失 | Commit #493 的 diff 中已確認 hooks 在 block 外（AliceLJY 確認）|
| 3. 5 個 unrelated fixes 包在一起 | scope drift | #498、#500、#510 已拆成獨立 PR（但未合併）|
| 4. 無測試 | 373 行無測試覆蓋 | → #506（Phase 4）處理，但 #506 有 mock 問題待修 |

---

## 五、需要問維護者的 3 個問題

### Q1：Phase 1 方向是否被接受？

經過 18 個 commits 的迭代，#493 的問題 1（usage markers）、問題 2（autoCapture guard）都已經修復。
**問題**：這個修復後的版本是否足夠作為下一個 Phase 1 PR 的基礎？還是 rwmjhb 需要重新 review？

---

### Q2：三個拆出去的 PR（#498、#500、#510）還沒合併，要怎麼處理？

**問題**：這三個 PR 全部還是 Open。建議：
1. 先合併這三個 PR 到 master
2. 再 rebase Phase 1 branch 到最新 master
3. 重新打 PR targeting master

**是否同意這個順序？還是有其他考量？**

---

### Q3：Codex 的 `isRecallUsed()` 兩個 bug 需要一併修嗎？

1. `id[-:]` pattern 導致 false positive（Line 335）
2. Summary path 缺少 `hasUsageMarker` 檢查（Line 346）

**問題**：這兩個在下一個 Phase 1 PR 中修？還是當作 Phase 2 的範圍？

---

## 六、Phase 1 執行流程（Step by Step）

```
Step 0：等 maintainer 回覆 Q1-Q3
         ↓
Step 1：三個拆出去的 PR 先處理
       如果 maintainer 同意 → 合併 #498、#500、#510 到 master
         ↓
Step 2：建立乾淨的 Phase 1 分支
       → 以最新 master 為基準（包含 #498/#500/#510 如果已合併）
       → 確認 Phase 1 內容不包含 unrelated fixes
       → 明確在分支內修復 Codex 的兩個 isRecallUsed() bug
       → force push 更新 #507 branch
         ↓
Step 3：確認 autoCapture guard 位置正確
       → Feedback hooks（agent_end p20、before_prompt_build p5、session_end p20）
          必須在 if (config.autoCapture !== false) 區塊「之外」
         ↓
Step 4：重新打 PR targeting master
       → PR 內清楚說明：Scope 只含 Phase 1、不包 unrelated fixes
       → 附上 18 個 commits 的完整 changelog
       → 說明 #498/#500/#510 各自單獨 merge 的情況
         ↓
Step 5：等 maintainer review
       → 根據回覆修復，直到 APPROVED
       → 合併
```

---

## 七、Phase 1 程式碼範圍（最終狀態）

**新增檔案**：
- `src/reflection-slices.ts`：新增 `isRecallUsed()` 函式（~95 行）

**修改檔案**：
- `index.ts`：`pendingRecall` Map + 3 個 hooks（~270 行）
- `src/smart-extractor.ts`：regex fix
- `src/retriever.ts`：source 參數傳遞 + recency guard
- `src/auto-capture-cleanup.ts`：boilerplate stripping

**不修改**（Phase 1 確認不動的）：
- `decay-engine.ts`
- `tier-manager.ts`
- `access-tracker.ts`
