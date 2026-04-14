# FEATURE_REQUESTS.md — 功能需求記錄

## 2026-04-09 — Proposal A 相關功能需求

### FR-001：多語言 confirmKeywords / errorKeywords 支援

**類型**：功能改進（語言覆蓋）

**背景**：`feedback-config.ts` 中的 `confirmKeywords` 和 `errorKeywords` 只覆蓋部分語言：
- 缺少繁體中文：「對的」、「沒錯」
- 缺少簡體中文：「确认」、「没错」、「不对」
- 缺少英文：「yes」、「correct」、「that's right」、「that's wrong」、「mistake」、「incorrect」

**需求描述**：
```typescript
confirmKeywords: [
  'yes', 'correct', "that's right", '没错', '對', '確認', '正確', 'right', '對的',
]
errorKeywords: [
  'mistake', 'incorrect', "that's wrong", '错', '不对', '錯誤', '不對', 'wrong',
]
```

**優先程度**：P2 — 多語言或多地區部署時，feedback 信號會有語言偏差。

**是否已實作**：否（從未進入 official master）

---

### FR-002：injected_count 上限機制（cap / decay）

**類型**：資源管理

**背景**：`injected_count` 每次 injection `++`，但從未有任何 cap、decay 或 reset 機制。長期運行後 metadata 可能膨脹。

**需求描述**：
- 方案 A：加入 `MAX_INJECTED_COUNT` 常數，達到上限後不再遞增
- 方案 B：加入 injected_count decay（每次 decay 時同步減少）
- 與現有 `MAX_SOURCES`/`MAX_HISTORY`/`MAX_RELATIONS` 保持一致模式

**優先程度**：P2 — 長期運行穩定性

**是否已實作**：否

---

### FR-003：recall-feedback 生命週期端到端測試

**類型**：測試基礎設施

**背景**：現有的 Phase 4 測試 (`feedback-config.test.mjs`, `bad-recall-count.test.mjs`) 都在測 mock，無法驗證真實程式碼行為。整個 `pendingRecall` → `agent_end` → `before_prompt_build scoring` → `importance update` 生命週期沒有端到端覆蓋。

**需求描述**：
建立完整的端到端測試，覆蓋場景：
1. 正常 injection → recall 使用 → confirm feedback → importance += 0.05
2. injection → 未被使用（miss）→ bad_recall_count += 1
3. injection → 被否定 → importance -= 0.10
4. 連續 miss >= 2 次 → composite score penalty 觸發

**優先程度**：P1 — 沒有端到端測試，無法確保 recall-feedback 系統正確運作。

**是否已實作**：否

---

### FR-004：last_confirmed_use_at 寫入 + staleInjected 正確邏輯

**類型**：Bug 修復 / 功能補完

**背景**：`last_confirmed_use_at` 從未被寫入任何值，導致 `staleInjected` 幾乎每次都是 true（錯誤判斷）。

**需求描述**：
1. 在 confirm path（記憶被成功使用並確認）時，正確寫入 `last_confirmed_use_at = Date.now()`
2. `staleInjected` 邏輯需依賴此欄位，確保只有真正一段時間未使用的 injection 才被視為 stale

**優先程度**：P0 — 此功能不完整會導致 recall feedback 系統信號失真。

**是否已實作**：否（core bug）

---

### FR-005：importance / Decay floor 矛盾解決方案裁決

**類型**：設計決策（需 AliceLJY 裁決）

**背景**：Feedback 的 importance floor 是 0.1，但 Decay engine 的 tier floor 是 Core=0.9、Working=0.7、Peripheral=0.5。當 Core tier 記憶被 feedback 降至 0.1 時，decay 和 importance 脫鉤。

**需求描述**：
- 方案 A：feedback floor 與 tier-decay floor 掛鉤：`importanceFloor = max(0.1, peripheralDecayFloor - 0.4)`
- 方案 B：decay floor 只約束 composite score，不約束 importance 欄位
- 方案 C：明確區分「重要性分數衰減」與「元数据重要性更新」概念

**優先程度**：P1 — 設計矛盾若不解決，長期會造成記憶行為不可預測。

**等待維護者確認**：是（需 AliceLJY 裁決）

---

### FR-006：配置 schema validation（含錯誤提示）

**類型**：可用性改進

**背景**：使用者錯誤設定 `confirmKeywords: "not an array"`（傳入 string 而非 array），目前是 silent fallback（用預設值），用戶可能以為自定義生效了。

**需求描述**：
- 在 `parsePluginConfig()` 加入 schema validation
- 拒絕時明確報錯（如：`"confirmKeywords must be an array, got string"`）而非 silent fallback
- 支援多語言錯誤訊息

**優先程度**：P3 — 可用性問題，debug 困難。

**是否已實作**：否
