# PR Status

*最後更新：2026-03-23 14:27 GMT+8*

---

## PR 狀態總覽

| PR | 分支 | 標題 | 狀態 | CI | URL |
|----|------|------|------|-----|-----|
| #40 | `pr/dual-track-dedup` | feat(kubejs): 實作雙軌 reverse_index 去重 | ✅ OPEN | 🔄 Running | https://github.com/jlin53882/Minecraft-translate/pull/40 |
| #41 | `pr/color-checker` | feat(checkers): 新增顏色字元校驗工具 | ✅ OPEN | 🔄 Running | https://github.com/jlin53882/Minecraft-translate/pull/41 |
| #42 | `pr/rich-text-shield` | feat(shared): 新增 rich_text_shield 脫殼模組 | ✅ OPEN | 🔄 Running | https://github.com/jlin53882/Minecraft-translate/pull/42 |

---

## 詳細資訊

### PR #40 — feat(kubejs): 實作雙軌 reverse_index 去重
- **分支**：`pr/dual-track-dedup`
- **Commit**：`f15ad45`
- **主要變更**：`kubejs_translator_clean.py` (+31 行)
- **描述**：新增雙軌 reverse_index 去重邏輯

### PR #41 — feat(checkers): 新增顏色字元校驗工具
- **分支**：`pr/color-checker`
- **Commit**：`c2097c1`
- **主要變更**：`color_char_checker.py` (+115 行)
- **描述**：檢查翻譯檔案中的非法顏色字元

### PR #42 — feat(shared): 新增 rich_text_shield 脫殼模組
- **分支**：`pr/rich-text-shield`
- **Commit**：`5d66f73`
- **主要變更**：`rich_text_shield.py` (+266 行)、整合進 kubejs 管線
- **描述**：Rich Text 保護層，翻譯前脫殼、翻譯後還原

---

## ⚠️ 注意：分支重疊問題

`pr/rich-text-shield` (#42) 的 commit 包含了 `pr/color-checker` (#41) 和 `pr/dual-track-dedup` (#40) 的 commit。
建議合併順序：#40 → #41 → #42

---

## CI 狀態

所有 3 個 PR 的 CI 都已觸發並運行中（2026-03-23 06:27 UTC）。
