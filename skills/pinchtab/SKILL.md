# pinchtab - 瀏覽器自動化控制技能

## 概述
控制 PinchTab 瀏覽器自動化服務，透過 CLI 或 HTTP API 操作 Chrome 瀏覽器。

## 安裝與設定

### 安裝
```bash
npm install -g pinchtab
```

### 開機自動啟動
```bash
# 建立啟動腳本
pinchtab server
```

### 檢查狀態
```bash
pinchtab health
pinchtab profiles    # 查看所有 profile
pinchtab instances   # 查看運行的實例
```

---

## ⚠️ 重要：Profile 持久化

### 問題
CLI 預設使用 `default` profile，**無狀態**——關閉後 cookies、login 全部消失。

### 解決方法
**必須明確指定 profile 名稱**：

```bash
# 建立命名 profile（只需一次）
pinchtab instance start --mode headed --profile github-login

# 之後使用相同 profile
pinchtab instance start --mode headed --profile github-login
```

### 已存在的 Profiles
| 名稱 | 用途 |
|------|------|
| `default` | 預設，無持久化 |
| `github-login` | GitHub/Google 登入資料 |

### Profile 管理指令
```bash
pinchtab profiles              # 列出所有 profile
pinchtab instance start --profile <name>   # 用指定 profile 啟動
```

---

## 常用指令速查

### 實例管理
| 指令 | 說明 |
|------|------|
| `pinchtab server` | 啟動控制服務 |
| `pinchtab instance start --mode headed --profile <name>` | 開啟有視窗瀏覽器 |
| `pinchtab instance start --mode headless --profile <name>` | 開啟無頭瀏覽器 |
| `pinchtab instance stop <instance-id>` | 停止實例 |
| `pinchtab instances` | 列出運行中的實例 |

### 瀏覽器操作
| 指令 | 說明 |
|------|------|
| `pinchtab nav <url>` | 導航到 URL |
| `pinchtab screenshot` | 截圖 |
| `pinchtab snap` | 取得 accessibility tree |
| `pinchtab click <ref>` | 點擊元素 |
| `pinchtab fill <selector> <text>` | 填寫輸入框 |
| `pinchtab type <ref> <text>` | 輸入文字 |
| `pinchtab eval <script>` | 執行 JavaScript |

### 進階操作
| 指令 | 說明 |
|------|------|
| `pinchtab text` | 提取頁面文字 |
| `pinchtab pdf -o output.pdf` | 匯出 PDF |
| `pinchtab find <query>` | 自然語言查詢元素 |

---

## 使用範例

### 範例 1：開啟已登入的 GitHub
```bash
# 1. 先確認 profile 存在
pinchtab profiles

# 2. 用已登入的 profile 開啟 headed 瀏覽器
pinchtab instance start --mode headed --profile github-login
```

### 範例 2：導航並截圖
```bash
pinchtab nav https://github.com
pinchtab screenshot
```

### 範例 3：自動化登入流程
1. `pinchtab nav https://github.com/login`
2. `pinchtab fill "#login_field" "your-email"`
3. `pinchtab fill "#password" "your-pass"`
4. `pinchtab click "Sign in"`

---

## HTTP API（進階）

### 端點
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/health` | 健康檢查 |
| POST | `/nav` | 導航 |
| POST | `/snap` | 截取 accessibility tree |
| POST | `/act` | 執行操作（點擊、填寫等） |
| POST | `/eval` | 執行 JavaScript |

### 範例
```bash
curl -X POST http://localhost:9867/nav \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

---

## 故障排除

| 問題 | 解決方式 |
|------|----------|
| 服務未啟動 | 執行 `pinchtab server` |
| 登入資料消失 | 確認使用 `--profile <name>` 而非 default |
| profile 已存在但無法啟動 | 先停止現有實例：`pinchtab instance stop <id>` |
| 連線被拒 | 確認服務運行於 localhost:9876 或 9867 |

---

## 與 OpenClaw 內建瀏覽器比較

| 特性 | OpenClaw browser | PinchTab |
|------|------------------|----------|
| 安裝 | 開箱即用 | 需 `npm install -g pinchtab` |
| Token 效率 | 普通 | 800 tokens/page（省 5-13x） |
| Profile | 單一固定 | 多個命名 profile |
| HTTP API | 無 | 有 |
| Skill | agent-browser | 需手動呼叫 CLI |
