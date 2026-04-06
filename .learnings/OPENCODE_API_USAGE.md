# OpenCode API 使用誤區（已驗證）

## 核心問題
OpenCode 不會主動搜尋相關分支、檔案路徑或專案結構，必須由呼叫者（OpenClaw）主動提供上下文，否則會找錯目標。

## 正確做法
每次呼叫 OpenCode 前，主動告知：
- 目標分支名稱（如 `feature/xxx`）
- 檔案完整路徑（如 `C:\Users\admin\Desktop\minecraft_translator_flet\...`）
- 任務背景（例如：這是 Minecraft 翻譯工具、這是 Discord bot）
- Git 狀態（当前在哪個 branch、是否有 uncommitted changes）

## 壞範例
```
"幫我 review 這個 PR"
→ OpenCode 自己猜，經常猜錯分支或路徑
```

## 好範例
```
"請 review 位於 C:\Users\admin\Desktop\minecraft_translator_flet 分支 feature/xxx 的翻譯邏輯，
目前 git branch 是 feature/xxx，請注意 reverse_index.py 的 replace rules"
```

---

*記錄時間：2026-04-04*
