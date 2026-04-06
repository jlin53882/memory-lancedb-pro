# Flet Logging 控制（0.82.2）

> **版本**：flet:0.82.2
> **來源**：https://docs.flet.dev/cookbook/logging/
> **日期**：2026-03-22

---

## Python 程式內控制

Flet Python 模組暴露了兩個 named loggers：
- `flet_core`
- `flet`

### 啟用詳細日誌

在 `ft.run()` 之前加入：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

這樣會同時啟用 `flet_core` 和 `flet` 的所有 DEBUG 訊息。

### 減少噪音

如果覺得太多，可以抑制 `flet_core` 的 DEBUG 输出，只保留 WARNING 以上：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("flet_core").setLevel(logging.INFO)
```

### 常見場景

| 需求 | 設定 |
|---|---|
| 完整除錯 | `logging.basicConfig(level=logging.DEBUG)` |
| 一般使用 | `logging.basicConfig(level=logging.WARNING)` 或預設（不設定） |
| 只看 flet_core 錯誤 | `getLogger("flet_core").setLevel(logging.ERROR)` |

---

## Fletd Server（日誌伺服器）

Fletd 是 Flet 內建的 Web 伺服器。

### 日誌等級環境變數

```bash
FLET_LOG_LEVEL=debug   # 或 info / warning / panic / fatal
```

### 寫入檔案

```bash
FLET_LOG_TO_FILE=true
```

日誌檔案位置：
- Windows：`%TEMP%\flet-server.log`
- macOS / Linux：`/tmp/flet-server.log`

### 與 Python logging 的關係

當 Python 程式中設定了 `logging.basicConfig(level=...)` 時，該等級會隱含傳遞給 Fletd，兩邊日誌等級同步。

---

## 實際應用場景

### 場景 1：開發時開啟詳細日誌

```python
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("Hello"))

ft.run(main)
```

### 場景 2：只想看錯誤

```python
import logging
logging.basicConfig(level=logging.ERROR)
```

### 場景 3：取得 Console Log 檔案路徑

```python
import flet as ft

async def main(page: ft.Page):
    log_file = await ft.StoragePaths().get_console_log_filename()
    with open(log_file, "r") as f:
        logs = f.read()
    page.add(ft.Text(logs))

ft.run(main)
```

---

## 與 0.28.3 的差異

| 功能 | 0.28.3 | 0.82.2 |
|---|---|---|
| `logging.basicConfig()` | ✅ 可用 | ✅ 可用 |
| `flet_core` logger | ✅ | ✅ |
| `flet` logger | ✅ | ✅ |
| `FLET_LOG_LEVEL` env | 可能有 | ✅ 支援 |
| `FLET_LOG_TO_FILE` env | 可能有 | ✅ 支援 |
| `StoragePaths().get_console_log_filename()` | 可能無 | ✅ 新增 API |

---

## 與 FLET_DEBUG_STRATEGY.md 的關係

在 two_project 中：
- 如果要取代 `page.on_error` + `exports/error.log` 的錯誤追蹤方案
- 可以改用 `logging.basicConfig(level=logging.DEBUG)` + `FLET_LOG_TO_FILE=true`
- 所有錯誤（包括 UI handler 例外）會寫入 `%TEMP%\flet-server.log`
- 比 `page.on_error` 更全面（`page.on_error` 無法捕獲 UI handler 例外）
