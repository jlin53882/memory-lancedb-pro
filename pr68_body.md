## 修復內容

修復 Issue #65 中的 11 項 CRITICAL 問題，並根據對抗式 OpenCode + Claude Code Review 結果進行了兩項增強：

### 修復清單

| 問題 | 修復狀態 | 說明 |
|------|---------|------|
| C-1 remaining 切片 | ✅ | 使用 `remaining[expected:]` + API 回傳多於預期時截斷並報錯 |
| C-2 retry 機制 | ✅ | 指數退避重試（3次 + jitter）|
| C-3 原文混入 | ✅ | `_untranslated` 標記 + caller 檢查標記後跳過快取寫入 |
| C-4 路徑遍歷 | ✅ | `os.path.abspath()` 驗證在 `output_root` 內 |
| C-5~C-10 ZIP bomb | ✅ | 6處加大小限制（50MB~100MB 閾值）|
| C-11 無限期迴圈 | ✅ | `no_progress_count` 追蹤，連續 3 次停滯則中斷 |

### 對抗稽核增強（OpenCode + Claude Review）

根據對抗式程式碼稽核結果，進行了以下增強：

1. **C-1 增強**：若翻譯 API 回傳多於預期（模型串接錯誤/JSON 截斷污染），多出的項目會被截斷並記錄錯誤，而非靜默遺失
2. **C-3 完整修復**：在 `lm_translator_shared_loop.py` 的 cache 寫入前檢查 `_untranslated` 標記，確保未翻譯的原項目不會寫入快取

## 驗證

- [x] pytest: **1204 passed, 1 skipped**（12.86s）
- [x] 對抗式 OpenCode + Claude Code Review 確認無新問題

## 關聯 Issue

- Issue #65: https://github.com/jlin53882/Minecraft-translate/issues/65
- Issue #66（待實作）: https://github.com/jlin53882/Minecraft-translate/issues/66
- Issue #67（待實作）: https://github.com/jlin53882/Minecraft-translate/issues/67

Closes #65
