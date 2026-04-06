# OpenCode Server 啟動

## Windows

```powershell
# 基本
opencode serve --port 4096 --hostname 127.0.0.1

# 允許外部連線
opencode serve --port 4096 --hostname 0.0.0.0
```

## 驗證

```powershell
Invoke-RestMethod http://127.0.0.1:4096/global/health
# {"healthy":true,"version":"1.3.13"}
```
