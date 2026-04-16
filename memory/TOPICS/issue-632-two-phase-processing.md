# Issue #632 收尾紀錄

**日期**: 2026-04-16
**議題**: Lock contention between upgrade CLI and plugin causes writes to fail
**PR**: https://github.com/CortexReach/memory-lancedb-pro/pull/639
**分支**: `jlin53882/test/phase2-upgrader-lock`

---

## 問題描述

### 根因
舊實作每處理一個 entry 都會呼叫 `store.update()`，導致：
- **N entries = N lock acquisitions**
- Plugin 在 auto-recall 時需要等數秒才能拿到 lock
- 造成 `auto-recall timed out after 60000ms`

### 問題程式碼位置
`memory-upgrader.ts` 的 `upgradeEntry()` 方法

---

## 解決方案：兩階段處理 (Two-Phase Processing)

### Phase 1: LLM Enrichment（無 lock）
- `prepareEntry()` 方法
- 執行 LLM 處理（最耗時的部分）
- **不需要 lock**，可並發執行

### Phase 2: DB Writes（單次 lock）
- `writeEnrichedBatch()` 方法
- 一次 lock 寫入所有 DB
- **每個 batch 只拿一次 lock**

### Lock 改善效果

| 情境 | 舊實作 | 新實作 | 改善 |
|------|--------|--------|------|
| 10 entries / batch=10 | 10 locks | **1 lock** | -90% |
| 25 entries / batch=10 | 25 locks | **3 locks** | -88% |
| 100 entries / batch=10 | 100 locks | **10 locks** | -90% |

---

## 修改的檔案

### 1. `src/memory-upgrader.ts`
**主要修改**：
- 新增 `EnrichedEntry` interface
- 新增 `prepareEntry()` - Phase 1：LLM 處理（無 lock）
- 新增 `writeEnrichedBatch()` - Phase 2：一次 lock 寫入
- 修改 `upgrade()` 為兩階段處理流程
- 移除舊的 `upgradeEntry()` 方法

**註解**：
- class 等級的 `REFACTORING NOTE`
- 各方法的詳細說明
- 批次處理內的 inline 註解

### 2. `test/upgrader-phase2-extreme.test.mjs`
**測試內容**：
- Test 1: Lock 次數驗證（10 entries = 1 lock）
- Test 2: LLM 失敗優雅降級
- Test 3: 混合成功/失敗處理
- Test 4: 批次邊界（25 entries = 3 locks）
- Test 5: 100 entries 壓力測試
- Test 6: 舊 vs 新實作比較

### 3. `test/upgrader-phase2-lock.test.mjs`
**測試內容**：
- 更新 Test 1 驗證新的（修復後的）行為
- 驗證每個 batch 只拿一次 lock

---

## Plan B 追蹤

**Issue #638**: Plan B: Compare-and-Swap (CAS) for Lock-Free Memory Upgrades
https://github.com/CortexReach/memory-lancedb-pro/issues/638

**說明**：
- 需要 schema migration（加 `version` 欄位）
- 需要修改 `store.update()` API
- 超出目前 PR 範圍
- 適合做為未來優化

---

## 測試執行

```bash
# 在 memory-lancedb-pro-test 目錄
node test/upgrader-phase2-extreme.test.mjs
node test/upgrader-phase2-lock.test.mjs
```

**結果**：全部測試通過 ✅

---

## 本地套用

已套用到本地 extension：
- `C:\Users\admin\.openclaw\extensions\memory-lancedb-pro\src\memory-upgrader.ts`

**jiti cache 清除**：
- `C:\Users\admin\AppData\Local\Temp\jiti` ✅
- `C:\Users\admin\AppData\Local\Temp\debug-jiti-*` ✅

---

## 注意事項

### 修改外掛程式碼後清除 jiti cache
根據 AGENTS.md 規則：
> 修改 plugins/ 下的 .ts 檔案後，必須先清除 `/tmp/jiti/` 目錄再重啟 openclaw gateway

### 測試檔案不要 inline mock 核心邏輯
根據過去踩坑經驗：
> 測試檔案內重新實作 local class 作為 mock，會導致即使實際程式碼邏輯改變，測試仍會通過（false pass）

---

## 參考連結

| 項目 | 連結 |
|------|------|
| PR #639 | https://github.com/CortexReach/memory-lancedb-pro/pull/639 |
| Issue #632 | https://github.com/CortexReach/memory-lancedb-pro/issues/632 |
| Issue #638 (Plan B) | https://github.com/CortexReach/memory-lancedb-pro/issues/638 |
