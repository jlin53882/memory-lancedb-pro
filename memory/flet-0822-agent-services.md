# Flet Services 速查手冊

> **版本標籤**：`flet:0.82.2`  
> **資料來源**：[docs.flet.dev/services](https://docs.flet.dev/services/)  
> **建檔日期**：2026-03-22  
> **說明**：每項 Service 包含用途、API 簽名（屬性/方法/事件）、程式範例、平台限制。

---

## 目錄

| # | Service | 狀態 |
|---|---------|------|
| 1 | [Accelerometer](#1-accelerometer) | ⚠️ 僅說明，無完整 API 文件 |
| 2 | [Barometer](#2-barometer) | ✅ |
| 3 | [Battery](#3-battery) | ✅ |
| 4 | [Camera](#4-camera) | ❌ 404 |
| 5 | [Filesystem](#5-filesystem) | ❌ 404 |
| 6 | [Geolocator](#6-geolocator) | ❌ 404 |
| 7 | [Gyroscope](#7-gyroscope) | ✅ |
| 8 | [Magnetometer](#8-magnetometer) | ✅ |
| 9 | [Notifications](#9-notifications) | ❌ 404 |
| 10 | [Permissions](#10-permissions) | ❌ 404 |
| 11 | [Share](#11-share) | ✅ |
| 12 | [Storage](#12-storage) | ❌ 404 |
| 13 | [TextToSpeech](#13-texttospeech) | ❌ 404 |

---

## 1. Accelerometer

### 用途
串流設備加速度感測器的原始讀數，單位為 m/s²（包含重力影響）。與 UserAccelerometer 不同，Accelerometer 回報的是未經後處理的物理感測器原始資料。

在地球表面，即使設備完全靜止，讀數仍為 9.8 m/s² 向上（因為重力向下）。可用於推斷設備朝向（水平/垂直/傾斜）。自由落體時回報零加速度。

### 平台限制
- ✅ Android
- ✅ iOS
- ✅ Web（忽略自訂取樣間隔）

### API 簽名（文件不完整，以下為推斷）

> ⚠️ **文件不完整**：此頁面缺少屬性/方法/事件定義，僅有說明文字。

```
// 推斷結構（與同類感測器一致性推斷）
屬性：
  - cancel_on_error: bool       // 感測器錯誤時是否取消串流
  - enabled: bool                // 是否啟用取樣
  - interval: Duration | None   // 取樣間隔（預設 200ms）

事件：
  - on_error: EventHandler[SensorErrorEvent]   // 感測器錯誤時觸發
  - on_reading: EventHandler[AccelerometerReadingEvent]  // 新讀數時觸發
```

事件內容：`AccelerometerReadingEvent` 包含 x, y, z 軸加速度（m/s²）與 timestamp。

---

## 2. Barometer

### 用途
串流氣壓計讀數（大氣壓力，單位 hPa），可用於高度計算與天氣體驗。

### 平台限制
- ✅ Android
- ✅ iOS
- ❌ Web 不支援
- ❌ Desktop 不支援
- ⚠️ iOS 忽略自訂取樣間隔

### iOS 特殊需求
需在 `Info.plist` 加入 `NSMotionUsageDescription` 金鑰，說明取用動作資料的原因，否則存取運動資料時會崩潰：

```toml
# pyproject.toml
[tool.flet.ios.info]
NSMotionUsageDescription = "This app requires access to the barometer to provide altitude information."
```

### API 簽名

```
繼承：Service
```

**屬性**

| 屬性 | 類型 | 說明 |
|------|------|------|
| `cancel_on_error` | `bool` | 感測器錯誤時是否取消串流（預設 `True`） |
| `enabled` | `bool` | 是否啟用取樣，關閉可停止串流 |
| `interval` | `Duration \| None` | 取樣間隔（預設 200ms，iOS 忽略） |

**事件**

| 事件 | 觸發時機 |
|------|---------|
| `on_error` | 平台回報感測器錯誤，`event.message` 為錯誤描述 |
| `on_reading` | 有新讀數時，內容包含 `pressure`（hPa）與 `timestamp`（微秒） |

### 範例

```python
import flet as ft

def main(page: ft.Page):
    def handle_reading(e: ft.BarometerReadingEvent):
        reading.value = f"{e.pressure:.2f} hPa"
        page.update()

    def handle_error(e: ft.SensorErrorEvent):
        page.add(ft.Text(f"Barometer error: {e.message}"))

    page.services.append(
        ft.Barometer(
            on_reading=handle_reading,
            on_error=handle_error,
            interval=ft.Duration(milliseconds=500),
        )
    )

    page.add(
        ft.Text("Atmospheric pressure (hPa)."),
        reading := ft.Text("Waiting for data..."),
    )

ft.run(main)
```

---

## 3. Battery

### 用途
提供設備電池資訊與狀態變化通知。

### 平台限制
- 跨平台支援（文件未標註特定限制，，推斷為 Android / iOS / Web / Desktop 皆支援）

### API 簽名

```
繼承：Service
```

**事件**

| 事件 | 觸發時機 |
|------|---------|
| `on_state_change` | 電池狀態改變（charging / discharging / full / unknown） |

**方法（均為 async）**

| 方法 | 回傳值 | 說明 |
|------|--------|------|
| `get_battery_level()` | `int \| None` | 取得電量百分比（0-100），不支援時回傳 `None` |
| `get_battery_state()` | `BatteryState` | 取得目前電池狀態列舉值 |
| `is_in_battery_save_mode()` | `bool` | 是否啟用省電模式 |

### 範例

```python
import flet as ft

async def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    async def refresh_info(e: ft.Event[ft.Button] = None):
        level = await battery.get_battery_level()
        state = await battery.get_battery_state()
        save_mode = await battery.is_in_battery_save_mode()
        info.value = (
            f"Battery level: {level}%\n"
            f"Battery state: {state.name}\n"
            f"Battery saver: {'ON' if save_mode else 'OFF'}"
        )

    async def on_state_change(e: ft.BatteryStateChangeEvent):
        print(f"State changed: {e.state}")
        await refresh_info()

    battery = ft.Battery(on_state_change=on_state_change)
    page.services.append(battery)  # 需保留 Service 參考

    page.add(
        ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    info := ft.Text(),
                    ft.Button("Refresh battery info", on_click=refresh_info),
                ],
            )
        )
    )
    await refresh_info()

ft.run(main)
```

---

## 4. Camera

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/camera/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 5. Filesystem

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/filesystem/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 6. Geolocator

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/geolocator/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 7. Gyroscope

### 用途
串流陀螺儀讀數，回報設備各軸旋轉速率，單位為 rad/s。

### 平台限制
- ✅ Android
- ✅ iOS
- ✅ Web（忽略自訂取樣間隔）

### API 簽名

```
繼承：Service
```

**屬性**

| 屬性 | 類型 | 說明 |
|------|------|------|
| `cancel_on_error` | `bool` | 感測器錯誤時是否取消串流（預設 `True`） |
| `enabled` | `bool` | 是否啟用取樣，關閉可停止串流 |
| `interval` | `Duration \| None` | 取樣間隔（預設 200ms，Web 忽略） |

**事件**

| 事件 | 觸發時機 |
|------|---------|
| `on_error` | 平台回報感測器錯誤，`event.message` 為錯誤描述 |
| `on_reading` | 有新讀數時，內容包含 x, y, z 旋轉速率（rad/s）與 timestamp（微秒） |

### 範例

```python
import flet as ft

def main(page: ft.Page):
    def handle_reading(e: ft.GyroscopeReadingEvent):
        reading.value = f"x={e.x:.2f} rad/s, y={e.y:.2f} rad/s, z={e.z:.2f} rad/s"
        page.update()

    def handle_error(e: ft.SensorErrorEvent):
        page.add(ft.Text(f"Gyroscope error: {e.message}"))

    page.services.append(
        ft.Gyroscope(
            on_reading=handle_reading,
            on_error=handle_error,
            interval=ft.Duration(milliseconds=100),
        )
    )

    page.add(
        ft.Text("Rotate your device to see gyroscope readings."),
        reading := ft.Text("Waiting for data..."),
    )

ft.run(main)
```

---

## 8. Magnetometer

### 用途
串流磁力計讀數，回報環境磁場強度（單位 µT）於各軸，可用於電子羅盤等應用。

### 平台限制
- ✅ Android
- ✅ iOS
- ❌ Web 不支援
- ❌ Desktop 不支援
- ⚠️ 務必處理 `on_error` 以偵測不支援的硬體

### API 簽名

```
繼承：Service
```

**屬性**

| 屬性 | 類型 | 說明 |
|------|------|------|
| `cancel_on_error` | `bool` | 感測器錯誤時是否取消串流（預設 `True`） |
| `enabled` | `bool` | 是否啟用取樣，關閉可停止串流 |
| `interval` | `Duration \| None` | 取樣間隔（預設 200ms） |

**事件**

| 事件 | 觸發時機 |
|------|---------|
| `on_error` | 平台回報感測器錯誤，`event.message` 為錯誤描述 |
| `on_reading` | 有新讀數時，內容包含 x, y, z 磁場強度（µT）與 timestamp（微秒） |

### 範例

```python
import flet as ft

def main(page: ft.Page):
    def handle_reading(e: ft.MagnetometerReadingEvent):
        reading.value = f"x={e.x:.2f} µT, y={e.y:.2f} µT, z={e.z:.2f} µT"
        page.update()

    def handle_error(e: ft.SensorErrorEvent):
        page.add(ft.Text(f"Magnetometer error: {e.message}"))

    page.services.append(
        ft.Magnetometer(
            on_reading=handle_reading,
            on_error=handle_error,
            interval=ft.Duration(milliseconds=200),
        )
    )

    page.add(
        ft.Text("Monitor the ambient magnetic field (µT)."),
        reading := ft.Text("Waiting for data..."),
    )

ft.run(main)
```

---

## 9. Notifications

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/notifications/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 10. Permissions

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/permissions/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 11. Share

### 用途
使用平台原生的分享面板分享文字、連結或檔案。

### 平台限制
- ✅ 全平台（Android / iOS / Web / Desktop）
- ⚠️ 從路徑分享檔案在 Web 上不支援

### API 簽名

```
繼承：Service
```

**方法（均為 async）**

| 方法 | 說明 |
|------|------|
| `share_text(text, *, title, subject, preview_thumbnail, share_position_origin, download_fallback_enabled, mail_to_fallback_enabled, excluded_cupertino_activities)` | 分享純文字 |
| `share_uri(uri, *, share_position_origin, excluded_cupertino_activities)` | 分享連結/URI |
| `share_files(files, *, title, text, subject, preview_thumbnail, share_position_origin, download_fallback_enabled, mail_to_fallback_enabled, excluded_cupertino_activities)` | 分享一或多個檔案 |

**主要參數說明**

| 參數 | 類型 | 說明 |
|------|------|------|
| `text` | `str` | 分享的文字內容 |
| `title` | `str \| None` | 分享面板標題 |
| `subject` | `str \| None` | 郵件主題（用於 mailto fallback） |
| `preview_thumbnail` | `ShareFile \| None` | 分享面板中顯示的縮圖 |
| `share_position_origin` | `Offset \| None` | 分享面板位置 |
| `download_fallback_enabled` | `bool` | 是否啟用下載 fallback（預設 `True`） |
| `mail_to_fallback_enabled` | `bool` | 是否啟用 mailto fallback（預設 `True`） |
| `excluded_cupertino_activities` | `Iterable[ShareCupertinoActivityType] \| None` | iOS/macOS 要排除的分享活動 |

**回傳值**
- 所有方法回傳 `ShareResult`，包含 `status` 與 `raw` 屬性

**ShareFile 建立方式**

```python
# 從記憶體（bytes）建立
ft.ShareFile.from_bytes(b"...", mime_type="text/plain", name="file.txt")

# 從檔案路徑建立（僅非 Web）
ft.ShareFile.from_path("/path/to/file.txt")
```

### 範例

```python
import os
import flet as ft

async def main(page: ft.Page):
    share = ft.Share()

    status = ft.Text()
    result_raw = ft.Text()

    async def do_share_text():
        result = await share.share_text(
            "Hello from Flet!",
            subject="Greeting",
            title="Share greeting",
        )
        status.value = f"Share status: {result.status}"
        result_raw.value = f"Raw: {result.raw}"

    async def do_share_uri():
        result = await share.share_uri("https://flet.dev")
        status.value = f"Share status: {result.status}"
        result_raw.value = f"Raw: {result.raw}"

    async def do_share_files_from_bytes():
        file = ft.ShareFile.from_bytes(
            b"Sample content from memory",
            mime_type="text/plain",
            name="sample.txt",
        )
        result = await share.share_files(
            [file],
            text="Sharing a file from memory",
        )
        status.value = f"Share status: {result.status}"
        result_raw.value = f"Raw: {result.raw}"

    async def do_share_files_from_paths():
        if page.web:
            status.value = "File sharing from paths is not supported on the web."
            return
        temp_dir = await ft.StoragePaths().get_temporary_directory()
        file_path = os.path.join(temp_dir, "sample_from_path.txt")
        with open(file_path, "wb") as f:
            f.write(b"Sample content from file path")
        result = await share.share_files(
            [ft.ShareFile.from_path(file_path)],
            text="Sharing a file from memory",
        )
        status.value = f"Share status: {result.status}"
        result_raw.value = f"Raw: {result.raw}"

    page.add(
        ft.SafeArea(
            ft.Column([
                ft.Row([
                    ft.Button("Share text", on_click=do_share_text),
                    ft.Button("Share link", on_click=do_share_uri),
                    ft.Button("Share file from bytes", on_click=do_share_files_from_bytes),
                    ft.Button("Share file from path", on_click=do_share_files_from_paths),
                ], wrap=True),
                status,
                result_raw,
            ])
        )
    )

ft.run(main)
```

---

## 12. Storage

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/storage/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 13. TextToSpeech

### 狀態
❌ **404** — 文件不存在於 `docs.flet.dev/services/texttospeech/`

> 此服務在 Flet 0.82.2 文件中無對應頁面，可能已移除或尚未建立文件。

---

## 404 Service 索引

以下 7 個 Service 文件在 `docs.flet.dev` 0.82.2 版本中**不存在**（直接跳過）：

| Service | URL |
|---------|-----|
| Camera | `https://docs.flet.dev/services/camera/` |
| Filesystem | `https://docs.flet.dev/services/filesystem/` |
| Geolocator | `https://docs.flet.dev/services/geolocator/` |
| Notifications | `https://docs.flet.dev/services/notifications/` |
| Permissions | `https://docs.flet.dev/services/permissions/` |
| Storage | `https://docs.flet.dev/services/storage/` |
| TextToSpeech | `https://docs.flet.dev/services/texttospeech/` |

---

## 平台支援總覽

| Service | Android | iOS | Web | Desktop |
|---------|---------|-----|-----|---------|
| Accelerometer | ✅ | ✅ | ✅ | — |
| Barometer | ✅ | ✅ | ❌ | ❌ |
| Battery | ✅ | ✅ | ✅ | ✅ |
| Camera | ❌ | ❌ | ❌ | ❌ |
| Filesystem | ❌ | ❌ | ❌ | ❌ |
| Geolocator | ❌ | ❌ | ❌ | ❌ |
| Gyroscope | ✅ | ✅ | ✅ | — |
| Magnetometer | ✅ | ✅ | ❌ | ❌ |
| Notifications | ❌ | ❌ | ❌ | ❌ |
| Permissions | ❌ | ❌ | ❌ | ❌ |
| Share | ✅ | ✅ | ✅ | ✅ |
| Storage | ❌ | ❌ | ❌ | ❌ |
| TextToSpeech | ❌ | ❌ | ❌ | ❌ |

> 「—」表示文件未明確說明；「❌」表示明確不支援或 404 無文件。
