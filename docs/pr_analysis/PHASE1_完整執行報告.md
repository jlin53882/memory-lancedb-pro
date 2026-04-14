# Proposal A Phase 1 完整執行報告（最終版）
> 整理日期：2026-04-13
> 工作目錄：`C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro`
> Branch：`feat/proposal-a-v3-clean`

---

## 📋 Codex + OpenCode 對抗審查結果

### 第一次 Codex 審查（原始程式碼）
| 發現 | 等級 | 狀態 |
|------|------|------|
| P2: suppression threshold 不一致（>=3 vs >=2）| P2 | ✅ 已修復 |
| P1: Summary path AND gate 太嚴格 | P1 | ✅ 已修復 |
| P2: pendingIngress 覆蓋 | P2 | Phase 2 scope，skip |

### 第二次 Codex 審查（修復後）
| 發現 | 等級 | 狀態 |
|------|------|------|
| P1: bad_recall_count double increment + delayed suppression | P1 | ✅ 已修復 |
| P2: Summary reverse match false positive | P2 | 需評估 |

---

## 🔧 完整修復列表（已 push）

| SHA | 內容 |
|-----|------|
| `b371f0c` | P0-1 pendingRecall TTL cleanup、P0-3 Summary AND gate、P0-2 race condition 已知限制 |
| `d3d0b71` | P2: suppression threshold >= 3 → >= 2 |
| `8990c9d` | P1: 移除 Summary path AND gate，偵測自然使用 |
| `d33fe19` | P1: align scoring penalty with injection increment (>= 2 → >= 1) |

---

## 📝 變更摘要 vs #507/#505

```
### 新增修復（相對於 #507/#505）

1. [b371f0c] pendingRecall TTL cleanup（10分鐘）- 防止記憶體洩漏
2. [b371f0c] isRecallUsed() Summary path - 移除 AND gate，偵測自然使用
3. [b371f0c] bad_recall_count race condition - 已知限制（已標註）
4. [d3d0b71] suppression threshold >= 3 → >= 2 - 與 scoring 對齊
5. [8990c9d] Summary path 獨立運作 - 不依賴 hasUsageMarker
6. [d33fe19] scoring penalty >= 2 → >= 1 - 與 injection increment 同步

### 架構驗證
- autoCapture block boundary ✅
- hooks 正確 registration ✅

### 已知限制
- bad_recall_count 非 atomic（需 Phase 2 store-layer compare-and-swap）
- Summary reverse match 有 false positive 風險（minor，Phase 2 優化）
- pendingIngress 覆蓋問題（Phase 2 scope）
```

---

## ❌ 仍需 James 執行

**Rebase 到 upstream/master**：
```bash
cd C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro
git fetch upstream
git rebase upstream/master
git push --force-with-lease
```