# Daily Notes — 完整工作流

## 設定（一次性）

### 1. 設定預設 vault
```bash
obsidian-cli set-default "VAULT_NAME"
obsidian-cli print-default --path-only  # 驗證
```

### 2. 確認 vault 位置
```bash
# macOS
cat ~/Library/Application\ Support/obsidian/obsidian.json

# Windows
type "%APPDATA%\obsidian\obsidian.json"
```

找到 `"open": true` 的 vault，確認名稱。

## 常見使用場景

### 寫日記
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- 吃了早餐")" --append
```

### 記錄任務
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- [ ] 完成報告")" --append
```

### 附加連結
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- [[Meeting Notes]]")" --append
```

### 時間戳記日誌
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- $(date +%H:%M) 開始開會")" --append
```

### 讀取特定日期
```bash
# 上週五
obsidian-cli print "$(date -d 'last friday' +%Y-%m-%d 2>/dev/null || date -v-friday +%Y-%m-%d).md"

# 3 天前
obsidian-cli print "$(date -d '3 days ago' +%Y-%m-%d 2>/dev/null || date -v-3d +%Y-%m-%d).md"
```

### 搜尋內容
```bash
obsidian-cli search-content "關鍵字"  # 搜尋所有筆記內容
obsidian-cli search "meeting"          # 搜尋筆記名稱
```

## 跨平台日期指令

| 系統 | 相對日期 | 指令 |
|------|----------|------|
| Linux/macOS | 昨天 | `date -d yesterday +%Y-%m-%d` |
| Linux/macOS | 上週五 | `date -d 'last friday' +%Y-%m-%d` |
| macOS | 3 天前 | `date -v-3d +%Y-%m-%d` |
| Windows | 昨天 | `powershell -Command "(Get-Date).AddDays(-1).ToString('yyyy-MM-dd')"` |

## 自訂資料夾

如果 vault 中的每日筆記放在子資料夾：
```bash
obsidian-cli daily && obsidian-cli create "Daily Notes/$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "內容")" --append
```
