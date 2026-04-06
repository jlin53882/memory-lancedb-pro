# 2026-03-17 問題處理總結

## 1. Memory 系統優化

### embedding 模型切換
| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| 模型 | nomic-embed-text | jina-v5-retrieval-test |
| 維度 | 768 | 1024 |
| dbPath | lancedb-pro | lancedb-pro-jina1024 |
| 遷移 | - | 96 筆舊記憶重新 embed |

### 記憶品質優化
| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| built-in memorySearch | enabled: true | **enabled: false** |
| minScore | 0.35 | **0.55** |
| hardMinScore | 0.45 | **0.60** |
| candidatePoolSize | 20 | **10** |
| captureAssistant | (無) | **false** |

### ingest_local.py 修改
- IGNORE_PATTERNS 加入 `SKILL.md`
- category 判定邏輯：
  - filename 含 "decision" → decision
  - filename 含 "reflection"/"log" → reflection
  - 其他 .md → fact

---

## 2. Image Model 修正

| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| imageModel | minimax-vl-01 (OAuth 錯誤) | **openrouter/auto** |

---

## 3. Embedded Agent Timeout 修正

| 項目 | 說明 |
|------|------|
| 問題 | MiniMax API 延遲導致 15 秒 timeout |
| 原因 | OpenClaw 原始碼硬編碼 `waitForEmbeddedPiRunEnd(timeoutMs = 15e3)` |
| 解決 | 修改 `model-selection-CU2b7bN6.js` 兩處：`15e3` → `120e3` |

---

## 4. Discord 頻道權限修正

| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| guilds.channels | 有限制頻道 | **移除限制** |
| plugins.allow | (無) | 加入 memory-lancedb-pro, openclaw-web-search |
| groupPolicy | (無) | **open**（不用標記就能回覆） |
| execApprovals | (無) | **enabled: true**（Discord 按鈕審批） |

### Discord groupPolicy 說明
- `open` = 不用標記就會回覆 ✅
- `all` = 需要標記才會回覆
- `allowlist` = 需要標記才會回覆

---

## 5. Obfuscated Command 偵測

| 項目 | 說明 |
|------|------|
| 問題 | OpenClaw 偵測到疑似 base64 編碼的代碼，擋下執行 |
| 解決 | 啟用 Discord execApprovals，讓審批可以用按鈕通過 |

---

## 6. 待驗證項目

- [ ] Discord 所有頻道是否都能正常回應
- [ ] Embedded agent timeout 是否從 15 秒延長到 120 秒
- [ ] imageModel 改為 openrouter/auto 後是否正常運作

---

## 6. 已記住的決策（ LanceDB ）

1. embedding 模型切換至 jina-v5-retrieval-test + re-embed 遷移
2. imageModel 改為 openrouter/auto
3. built-in memorySearch 再次關閉
4. 召回參數調整
5. captureAssistant: false
6. ingest_local.py 優化
7. MiniMax API timeout 處理機制
