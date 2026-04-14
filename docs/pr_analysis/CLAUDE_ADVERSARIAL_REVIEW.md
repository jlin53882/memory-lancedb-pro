

# Proposal A 對抗性 Code Review 報告

## 執行摘要

經過對 PR #493/#505/#506/#507 分析文件與官方程式碼的交叉比對，發現**所有 PR 均為 closed 狀態從未合併進 official master**，Proposal A 功能事實上**從未交付**。更嚴重的是，官方程式碼中 `bad_recall_count` 只有 `= 0` 的寫入（reset），**完全找不到任何 `+ 1` 遞增邏輯**，導致 `badCount >= 2`  penalty 觸發條件永遠不可能滿足。此外，`importance floor 0.1` 與 Decay floor (Core=0.9/Working=0.7/Peripheral=0.5) 存在根本性設計矛盾，會造成 decay 分數計算與重要性回饋的目標互相衝突。

---

## 嚴重問題（必須修復才能繼續）

### 問題 1：所有 PR 均未合併 — 功能根本不存在

- **檔案/位置**：PR #493/#505/#506/#507 全部為 `closed` 狀態，無一是 `merged`
- **問題描述**：
  ```
  PR #493: closed (2026-04-04)
  PR #505: closed (2026-04-05)
  PR #507: closed (2026-04-05)
  PR #506: open（但 AliceLJY 給了 CHANGES_REQUESTED，尚未關閉）
  ```
  官方 `master` 分支從未收到任何 Proposal A 代码。整個 feature 是「未實現的願望清單」。
- **觸發條件**：查閱 GitHub PR 頁面狀態即可確認
- **嚴重程度**：5/5
- **修復建議**：
  1. 確認為何 PR 被關閉而非合併（應是先close落後分支再重新導向？）
  2. 重建正確的分支鏈：`feat/proposal-a-v3-clean` →  target `master`
  3. 逐一解決 AliceLJY 的 CHANGES_REQUESTED 後重新提出
- **是否需要維護者確認**：是 — 需確認 branch 策略是否正確

---

### 問題 2：`bad_recall_count` 只有 reset，**從未 increment**

- **檔案/位置**：`memory-lancedb-pro-master/src/tools.ts`（官方）與 `memory-lancedb-pro/src/tools.ts`（workspace）
- **問題描述**：
  在整個官方程式碼庫中，`bad_recall_count` 只有 `= 0` 的賦值（smart-extractor.ts 第 1002/1100/1164/1220 行，tools.ts 第 595/843/934/1872 行），**完全找不到任何 `bad_recall_count + 1` 的遞增寫入**。
  
  這意味著：
  - PR #507 PR 說「bad_recall_count increments correctly in error/miss paths」是**誤導** — 該實作從未進入 master
  - `badCount >= 2` 的 penalty threshold **永遠不可能觸發**，因為計數器從未超過 0
  - Phase 1 設計的四個信號中，第三個（連續未使用 >=2次）**在官方程式碼中是一個 dead code path**
- **嚴重程度**：5/5
- **修復建議**：
  - 在 `before_prompt_build` hook 的 miss path 中，正確遞增 `bad_recall_count`：
    ```typescript
    const current = parseSmartMetadata(entry.metadata);
    const nextBad = current.bad_recall_count + 1;
    // 寫回 metadata
    ```
  - 並非只有 reset (=0)；confirm path 才做 reset，miss path 做 +1
- **是否需要維護者確認**：是 — 需確認這是實作遺漏還是設計理解錯誤

---

### 問題 3：`Decay floor (0.5~0.9) 與 Feedback floor (0.1) 設計矛盾`

- **檔案/位置**：
  - `decay-engine.ts`：`coreDecayFloor=0.9`, `workingDecayFloor=0.7`, `peripheralDecayFloor=0.5`（第 59-61 行）
  - `feedback-config.ts`： importance 下限 0.1（來自 Proposal A 規格）
- **問題描述**：
  ```
  Decay engine 設計：
    Core tier → decay 分數永不得低於 0.9
    Working tier → decay 分數永不得低於 0.7  
    Peripheral tier → decay 分數永不得低於 0.5
  
  Feedback 設計：
    importance -= 0.10, floor at 0.1
  ```
  
  矛盾點：
  1. 假設一個 Core memory 的 `importance = 0.7`，decay 分數 component 為 `0.3×importance = 0.21`，加上 `0.4×recency + 0.3×frequency` 後，最終 composite 仍是有意義的 decayed value
  2. 但若 feedback 將 `importance` 压到 0.1，decay engine 的 `effectiveHL = halfLife × exp(1.5 × 0.1)` 會幾乎不衰减（半衰期幾乎等於 base halfLife）
  3. **更重要**：若 importance 低至 0.1 而 tier 仍是 Core，decay floor 0.9 會「強行」把 composite 分數拉高，但 intrinsic component (`0.3 × 0.1 × confidence = 0.03`) 仍然很低，造成 components 之間的荒謬比例
- **嚴重程度**：4/5
- **修復建議**：
  - 方案 A：feedback floor 應與 tier-decay floor 掛鉤：`importanceFloor = max(0.1, peripheralDecayFloor - 0.4)`
  - 方案 B：decay floor 只約束 composite score，不約束 importance 欄位本身
  - 方案 C：明確區分「重要性分數衰減」與「元数据重要性更新」兩個概念，在文檔中說明差異
- **是否需要維護者確認**：是 — 這是高層次設計取捨，需 AliceLJY 裁決

---

### 問題 4：`autoCapture: false` 區塊邊界回歸 — 功能開關失效

- **檔案/位置**：PR #507 / #505 中 `index.ts` 的 hook 註冊位置
- **問題描述**：
  PR #507 的 Codex P1 Badge 指出：
  > `if (config.autoCapture !== false)` 區塊在 `api.on("agent_end", ...)` 以後**沒有正確關閉**，導致後續程式碼被錯誤地 conditional 化。停用 auto-capture 的設定會一併停用無關的功能（包括新的 recall-feedback hooks、self-improvement hooks 等）。
  
  這是一個**功能性回歸（behavioral regression）**：設定 `autoCapture: false` 的使用者會發現不只 auto-capture 被停用，連 `selfImprovement` 等其他功能也一起被關掉。
  
  PR #505 的 Issue Comment 也描述了同樣的 bug，並聲稱已修復，但 PR #505 本身是 closed 狀態，修復從未進入 master。
- **觸發條件**：
  ```javascript
  // openclaw.plugin.json
  {
    "autoCapture": false,
    "selfImprovement": { "enabled": true }
  }
  }
  // 預期：selfImprovement 正常運行
  // 實際：由於 block boundary bug，selfImprovement 也被停用
  ```
- **嚴重程度**：4/5
- **修復建議**：
  - 在 feedback hooks 區段**之前**，確認 `if (config.autoCapture !== false)) {` 的 `}` 有正確閉合
  - 重點：確認每個獨立的 hook 註冊都在正確的 scope 层级
- **是否需要維護者確認**：是 — 需驗證修復後的 code path 是否正確

---

### 問題 5：Phase 4 單元測試**兩個測試文件在測 mock 而非真實程式碼**

- **檔案/位置**：`test/feedback-config.test.mjs`、`test/bad-recall-count.test.mjs`
- **問題描述**：
  AliceLJY 在 PR #506 的 CHANGES_REQUESTED 中明確指出：
  > `feedback-config.test.mjs` — **problem**: re-implements `FeedbackConfigManager` as a local class in the test file. This tests that the mock works, not that the actual implementation is correct.
  > `bad-recall-count.test.mjs` — **same problem**: `computeNextBadCount` is defined inline in the test.
  
  **後果**：如果實際 source code 的實作邏輯與 mock 不同，測試仍會通過（false pass）。這是測試金字塔的基礎設施級缺陷。
  
  唯一的例外是 `isRecallUsed.test.mjs` — 這個檔案有**正確地**從 `../src/reflection-slices.ts` import 真正的 function 來測試。
- **觸發條件**：
  - `FeedbackConfigManager.computeImportanceDelta()` 的實際實作做了任何修改（改變計算邏輯或邊界條件）
  - `computeNextBadCount` 在實際程式碼中並不存在（它是 mock 的名稱）
  - 上述兩種情況下，測試都會給出虛假的 pass
- **嚴重程度**：4/5
- **修復建議**：
  1. 重寫 `feedback-config.test.mjs`：直接 import `FeedbackConfigManager` 從 `../src/feedback-config.js`
  2. 重寫 `bad-recall-count.test.mjs`：先確認 `computeNextBadCount` 的實際實作位置（可能根本不存在於 source），若不存在則調整測試策略
  3. 確保所有 test 都是**直接測試 source code**，而非測試 inline mock
- **是否需要維護者確認**：是 — 需 AliceLJY 確認此要求

---

## 中等問題（建議修復）

### 問題 6：isRecallUsed 中「记得」重複出現

- **檔案/位置**：`reflection-slices.ts` 第 377-378 行
- **問題描述**：`usageMarkers` 陣列中 `"记得"` 出現兩次（陣列中第 356 和 357 行）。輕量 bug。
- **嚴重程度**：1/5
- **修復建議**：刪除重複的 `"记得"` 項目

---

### 問題 7：`"not right"` 在 errorKeywords 中造成 false positive

- **檔案/位置**：`feedback-config.ts` 第 68 行
- **問題描述**：
  `errorKeywords: ['錯誤', '不對', 'wrong', 'not right']`
  
  當用戶說：
  > "That's not right — the meeting is at 3pm, not 2pm"
  
  這句話的意圖是「你說錯了時間（對 memory 的否定確認）」，但也有可能只是在「糾正一個具體事實」而非「否定記憶」。
  
  目前 `isErrorKeyword()` 使用 substring match（`toLowerCase().includes()`），會把「not right」當作 error signal。
  
  **但更重要**：「not right」作為 error keyword 會與 `isRecallUsed()` 的 summary branch 产生竞争：
  - agent 回應："Based on the memory, the meeting is at 2pm" （記憶被使用了，有 summary match）
  - 用戶回應："That's not right, it's at 3pm" （同時匹配 `errorKeywords` 和潜在的 confirm intent）
  - **結果**：importance -= 0.10，而不是 +0.05（use）— 等同懲罰了被使用的記憶
- **嚴重程度**：3/5
- **修復建議**：
  - 改用更精確的 error keyword：`['錯誤的', '不對的', 'wrong answer', 'incorrect']` 而非 `['wrong', 'not right']`
  - 或增加 context 判斷：只有當回應中包含被注入的 memory ID/摘要時，「not right」才被視為 error keyword
- **是否需要維護者確認**：是 — 需確認 keyword 設計意圖

---

### 問題 8：Summary match 分支**缺少 hasUsageMarker 檢查**

- **檔案/位置**：`reflection-slices.ts` 第 393-410 行
- **問題描述**：
  Codex P2 Badge 指出的問題：
  > The summary branch returns `true` on any verbatim summary hit of length >=10 **without checking `hasUsageMarker`**. This diverges from the function contract... so long responses that incidentally echo injected summary text will be treated as confirmed recall usage.
  
  ID path：
  ```typescript
  if (hasSpecificRecall) {  // AND gate
    for (const marker of usageMarkers) {
      if (responseLower.includes(marker)) return true;
    }
  }
  ```
  
  Summary path：
  ```typescript
  if (injectedSummaries && injectedSummaries.length > 0) {
    // 直接 return true，沒有 hasUsageMarker 檢查
    if (summaryLower.length >= 10 && responseTrimmedLower.includes(summaryLower)) return true;
  }
  ```
  
  這導致：如果用戶的回應**只是巧合地包含了一段注入的 summary text**（>=10 字元），就會被視為「記憶被使用」，即使 agent 完全沒有意識到這個記憶。
- **嚴重程度**：3/5
- **修復建議**：在 summary match branch 也加入 `hasUsageMarker` 檢查，或至少要求 `hasSpecificRecall = true`（即 summary match 需搭配 ID match，而非單獨成立）
- **是否需要維護者確認**：是 — 需確認這是 intended behavior 還是 bug

---

### 問題 9：`id[-:]` pattern 導致過度匹配

- **檔案/位置**：PR #506 分析文件提及（位於 `reflection-slices.ts` 的 usage marker regex）
- **問題描述**：
  如果 usage marker detection 包含 `id[-:]` pattern，則任何包含 `id-abc123` 這類常見 ID 格式的回應，都會滿足 `hasUsageMarker = true`。這使得 `hasMatchingId && hasUsageMarker` 的 AND 檢查實際上變成**只有** `hasMatchingId`，失去了 marker 的 second-factor 驗證意義。
- **觸發條件**：用戶說 "please use id-abc123" → 直接匹配 ID，marker 也是 true
- **嚴重程度**：2/5
- **修復建議**：
  - 從 usage marker regex 中移除 `id[-:]`
  - 或要求 ID 匹配**同時**要有具體的 usage marker phrase（而非僅有 ID 字串）
- **是否需要維護者確認**：否

---

### 問題 10：關鍵字缺乏簡體/繁體覆蓋

- **檔案/位置**：`feedback-config.ts` 第 67-68 行
- **問題描述**：
  ```typescript
  confirmKeywords: ['是對的', '確認', '正確', 'right']
  errorKeywords: ['錯誤', '不對', 'wrong', 'not right']
  ```
  
  問題：
  - **缺少繁體**：「是對的」是簡體，「對的」才是正體。繁體用戶說「是對的」不會匹配
  - **缺少簡體**：「確認」繁體是正體，但簡體用戶說「确认」不會匹配
  - **缺少英文 confirm**：「yes」/「correct」/「that's right」等常見表達未覆蓋
  - **缺少英文 error**：「that's wrong」/「incorrect」/「mistake」未覆蓋
  
  在一個多語言或多地區的部署中，這會導致回饋信號的**語言偏差**：簡體用戶的確認被忽略，繁體用戶的錯誤也被忽略。
- **嚴重程度**：2/5
- **修復建議**：
  ```typescript
  confirmKeywords: [
    '是對的', '確認', '正確', 'right',  // 現有
    'yes', 'correct', "that's right", '没错', '對',  // 新增
  ]
  errorKeywords: [
    '錯誤', '不對', 'wrong', 'not right',  // 現有
    'mistake', 'incorrect', "that's wrong", '错', '不对',  // 新增
  ]
  ```
- **是否需要維護者確認**：是 — 需確認多語言覆蓋範圍

---

## 輕微問題（可選修復）

### 問題 11：Branch拓撲錯誤導致合併衝突風險

- **問題描述**：PR #507/#505/#506 都 targeting master 且修改同樣檔案，若同時合併會產生無法預測的 diff conflicts
- **修復建議**：建立 stack chain：`feat/proposal-a-v3-clean` → `feat/proposal-a-v3-configurable-v2` → `feat/proposal-a-v3-tests`

### 問題 12：unrelated bug fixes 混入同一 PR

- **問題描述**：AliceLJY 在 PR #507 指出「please separate them into their own commits or PRs」
- **修復建議**：分離獨立的 bugfix 到各自 PR

### 問題 13：`injected_count` 單向膨脹無明確上限

- **問題描述**：每次 injection，`injected_count++` 但從未有任何 decay 或 reset 機制。長期運行後可能造成 metadata bloat。
- **修復建議**：加入 metadata array size cap（與 `MAX_SOURCES`/`MAX_HISTORY`/`MAX_RELATIONS` 同樣模式）

---

## 對抗性視角：維護者會問什麼？

### AliceLJY 可能問的尖銳問題

1. **「這些 PR 從未合併進 master。你實際上在請求我審查一個已經失效三天的程式碼。你現在的目標分支是什麼？」**
   — 這個問題直接戳破了「PR chain」的虛假表象。

2. **「你說 bad_recall_count increments correctly，但我們查閱官方程式碼完全看不到 increment 邏輯。請給我出具體的檔案路徑和行號。」**
   — 需要作者提供能對應到 actual committed code 的具體指標。

3. **「你的 importance floor 是 0.1，但 decay floor 是 0.5~0.9。當 importance 被压到 0.1 時，decay engine 的 intrinsic component 是 0.03，而 tier floor 是 0.9。這兩個數字在物理意義上代表什麼？你有沒有做過任何 end-to-end 的 simulation 來證明這個設計不會震盪？」**

4. **「Phase 4 的兩個測試文件在測 mock，這意味著你沒有辦法透過 CI 來驗證實際程式碼的正確性。你打算什麼時候重寫這些測試？」**

5. **「autoCapture block boundary 的 bug 在 PR #505 聲稱已修復，但 PR #505 是 closed 未合併。你如何向我證明這個 bug 在當前代碼中不存在？」**

6. **「你在一個 PR 中混合了 feature code 和 8 個 bugfixes，其中一些 bugfixes（如 Bug 6 的 rerankApiKey env resolution）與 feedback feature 完全無關。請問你什麼時候會把它們分離開？」**

---

## 對抗性視角：邊界條件攻擊

### 1. 空輸入 / 最短回應
```
輸入：agent 回應 "Hi"（<= 24 字元）
預期：isRecallUsed() = false（設計如此）
實際：isRecallUsed() = false ✅

變體：用戶說 "yes"（3 字元）
預期：isConfirmKeyword() 應能捕獲
實際：confirmKeywords 中 "yes" 不存在 → 可能漏確認
```

### 2. 特殊字元與 Unicode 混淆
```
輸入：用戶回應 "that's not right✔"
檢測："not right" 是 error keyword
結果：importance -= 0.10
問題：✔ emoji 可能干擾 substring match，但 "not right" 仍在
```

### 3. 長文本與 embedding 噪音
```
輸入：agent 回應 5000 字元的分析報告，
      其中隨機包含 "id-abc123" 和 "according to"
預期：isRecallUsed() = true（ID + marker）
實際：可能正確，但 summary match branch 
      在無 usage marker 情況下也可能觸發
```

### 4. 併發多 agent 環境
```
場景：sessionKey = "sess-1"，但有 agent-A 和 agent-B 同時運行
設計：pendingRecall 使用 "sessionKey:agentId" 複合鍵
問題：如果 agentId 是可變的（如動態分配），
      複合鍵的唯一性可能受損
建議：驗證 agentId 在 plugin lifecycle 中是否 stable
```

### 5. 配置錯誤時的靜默失敗
```
輸入：plugin config 中 feedback.confirmKeywords = "是對的"（string，非 array）
實際：
  - FeedbackConfigManager.fromRaw() 有 Array.isArray() 保護 → 用預設值
  - 但 parsePluginConfig() 對 raw.confirmKeywords 的處理：
      Array.isArray(raw.confirmKeywords)
        ? raw.confirmKeywords.filter(...)
        : ['是對的', '確認', '正確', 'right']  // 仍是 default
  所以有保護。但若用戶錯誤配置為：
  confirmKeywords: { "words": ["是對的"] }  // 錯誤的 object
  Array.isArray() → false → 用 default
  這不是 crash，是 silent fallback，但用戶可能以為自定義生效了
```

### 6. 極端 importance 值
```
場景：memory importance = 1.0（最大）
  → feedback "error" → importance -= 0.10 → 0.9
  → 再一次 error → importance -= 0.10 → 0.8
  → ...
  → 直到 floor 0.1，但 Core tier decay floor = 0.9
  
問題：在第 8 次 error 後，importance = 0.2，但仍是 Core tier
      decay engine 的 effectiveHL 會變長（importance 影響 half-life）
      但 tier promotion 的 importance threshold 是 0.8 (coreImportanceThreshold)
      此時若 composite 足夠高，仍會維持 Core tier
      但 importance 已降至 0.2 <- 這是一個邏輯不一致的狀態
      
建議：tier 應隨 importance 同步調整，而非獨立變化
```

---

## 建議的下一步

### 立即行動（修復阻塞性問題）

1. **確認為何 PR 被關閉** — 先在 issue #445 或直接聯繫 AliceLJY，確認分支策略。PR #507/#505/#506 的問題都是 branch topology 和代碼質量的問題，需要先解決這些才能重新提出有意義的 PR。

2. **重現 bad_recall_count increment 邏輯** — 這是 Phase 1 的核心 bug，需在 `before_prompt_build` hook 的 miss path 中正確實作 `bad_recall_count + 1`。

3. **修復 autoCapture block boundary** — 確認 `if (config.autoCapture !== false)) { ... }` 的 scope 正確閉合，所有 feedback/session hooks 在 if block 之外。

4. **重寫兩個 mock-based 測試文件** — 改為 import 真實程式碼，確保 CI 能驗證實際行為。

### 中期行動（設計決策）

5. **解決 Decay floor vs Feedback floor 矛盾** — 這需要 AliceLJY 參與的高層次設計決策，決定 importance 的 floor 是否應該與 tier 掛鉤。

6. **補充多語言關鍵字覆蓋** — 避免語言偏差導致回饋信號失效。

### 長期行動（架構完善）

7. **建立完整的端到端測試** — 測試 `pendingRecall` → `agent_end` → `before_prompt_build scoring` → `importance update` 的完整生命週期，而非各個 isolated unit test。

8. **考慮 injected_count 的 decay 或 cap 機制** — 防止 metadata bloat。