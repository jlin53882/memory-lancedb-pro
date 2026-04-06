# Flet Auth 授權與 Services — 學習筆記

> 來源：Flet 0.82.2 原始碼  
> 路徑：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\`  
> 涵蓋：auth / auth/providers / controls/services  

---

## Auth 系統架構

### 核心類繼承關係

```
Authorization（抽象介面）
    │
    └── AuthorizationService（實作）
            │
            ├── OAuthProvider（抽象設定類）
            │       ├── GitHubOAuthProvider
            │       ├── GoogleOAuthProvider
            │       ├── Auth0OAuthProvider
            │       └── AzureOAuthProvider
            │
            ├── OAuthToken（資料類）
            ├── User（dict 擴展）
            └── Group（dict 擴展）
```

### Authorization 抽象介面（auth/authorization.py）

位於第 1–44 行，定義了 OAuth 授權合約的 4 個抽象方法：

| 方法 | 用途 |
|------|------|
| `dehydrate_token(saved_token)` | 從已持久化的 token 恢復狀態（反序列化 + 刷新） |
| `get_token()` | 取得當前 token，自動在過期時刷新 |
| `get_authorization_data()` | 產生授權 URL 與 CSRF state（用於登入重導向） |
| `request_token(code)` | 用授權碼交換 access/refresh token |

所有方法皆為 `async`，`NotImplementedError` 驅使子類實作。

### AuthorizationService 實作（auth/authorization_service.py）

#### 建構子（第 48–72 行）

```python
def __init__(
    self,
    provider: OAuthProvider,
    fetch_user: bool,
    fetch_groups: bool,
    scope: Optional[list[str]] = None,
) -> None:
```

- `scope` 會自動合併 `provider.scopes`、`provider.user_scopes`（若 fetch_user）及 `provider.group_scopes`（若 fetch_groups）
- 內部維護 `self.__token: Optional[OAuthToken]` 及 `self.user: Optional[User]`

#### PKCE 支援（第 88–100 行，`get_authorization_data`）

使用 `oauthlib.oauth2.WebApplicationClient` 產生授權 URL，並傳入：
- `code_challenge` / `code_challenge_method`：PKCE 挑戰
- `code_verifier`（在 `OAuthProvider` 初始化時設定）
- `authorization_params`：額外 query 參數

#### Token 交換（第 110–126 行，`request_token`）

- 使用 `httpx.AsyncClient`（follow_redirects=True）POST 到 `token_endpoint`
- 透過 `WebApplicationClient.prepare_request_body()` 建構 `application/x-www-form-urlencoded` 請求體
- 包含 `code_verifier`（若使用 PKCE）

#### Token 刷新（第 182–215 行，`__refresh_token`）

- 僅在 `expires_at` 已過且存在 `refresh_token` 時才執行
- 刷新時若 provider 未回傳新 `refresh_token`，保留舊的（避免覆蓋為 None）
- 所有 OAuth HTTP 請求皆帶 `User-Agent: Flet/{flet_version}`

#### User/Groups 抓取（第 128–162 行，`__fetch_user_and_groups`）

1. 優先呼叫 `provider._fetch_user()`（provider 特化實作，如 GitHub API）
2. 若回傳 `None` 且 provider 有 `user_endpoint`，則用通用方式抓取
3. 若 `fetch_groups=True`，再呼叫 `provider._fetch_groups()`
4. **注意**：使用 `user_endpoint` 時，`user_id_fn` 為必填，否則拋 `ValueError`

### OAuthToken 資料類（auth/oauth_token.py）

| 欄位 | 說明 |
|------|------|
| `access_token` | 主存取權杖 |
| `refresh_token` | 刷新權杖（可選） |
| `expires_in` | 過期秒數 |
| `expires_at` | 絕對過期時間戳（`time.time()` 格式） |
| `token_type` | 通常為 "Bearer" |
| `scope` | 授權範圍列表 |

- `to_json()`：使用自訂 `EmbedJsonEncoder` 序列化（第 35–37 行）
- `from_json()`：反序列化重建實例（第 42–52 行）

### User 類（auth/user.py）

- 繼承自 `dict`，是個**可變映射**（provider 原生欄位全存入底層 dict）
- 標準化欄位：`id: str`、`groups: list[Group]`
- `id` 由 `user_id_fn(provider 回應)` 產生，而非直接取自 dict key

### Group 類（auth/group.py）

- 同樣繼承 `dict`，存放 provider 原生群組資料
- 標準化欄位：`name: str`

---

## OAuthProvider（Google / GitHub / Auth0 / Azure）

### OAuthProvider 基類（auth/oauth_provider.py，第 54–139 行）

#### 建構子參數

| 參數 | 用途 |
|------|------|
| `client_id` / `client_secret` | OAuth 應用程式憑證 |
| `authorization_endpoint` | 授權端點 URL |
| `token_endpoint` | Token 端點 URL |
| `redirect_url` | 回调 URL（須與 provider 註冊一致） |
| `scopes` | 基礎 OAuth 範圍 |
| `user_scopes` | 抓取用戶資料所需的額外範圍 |
| `group_scopes` | 抓取群組所需的額外範圍 |
| `user_endpoint` | 用戶資料端點（通用抓取模式） |
| `user_id_fn` | 從 user_endpoint 回應提取 user id 的函式 |
| `code_challenge` / `code_challenge_method` | PKCE 挑戰 |
| `code_verifier` | PKCE 驗證器 |
| `authorization_params` | 附加到授權 URL 的額外 query 參數 |

#### 兩個 Hook 點

```python
async def _fetch_user(self, access_token: str) -> Optional[User]:
    # Provider 特化實作（預設回傳 None）
    return None

async def _fetch_groups(self, access_token: str) -> list[Group]:
    # Provider 特化實作（預設回傳空列表）
    return []
```

### GitHubOAuthProvider（providers/github_oauth_provider.py）

- **端點**：`https://github.com/login/oauth/authorize` 與 `/access_token`
- **User scopes**：`read:user`、`user:email`
- **Group scopes**：`read:org`（讀取團隊）
- `_fetch_user()`：呼叫 `/user` API，並二次請求 `/user/emails` 找 `primary=True` 的 email（第 44–77 行）
- `_fetch_groups()`：呼叫 `/user/teams` API，對應 GitHub Teams（第 28–43 行）
- Header 攜帶 `Authorization: Bearer {token}` + `User-Agent: Flet/{version}`

### GoogleOAuthProvider（providers/google_oauth_provider.py）

- **端點**：`https://accounts.google.com/o/oauth2/auth`、`https://oauth2.googleapis.com/token`
- **User scopes**：`userinfo.email`、`userinfo.profile`（OpenID Connect）
- **User endpoint**：`https://www.googleapis.com/oauth2/v3/userinfo`（OIDC userinfo 端點）
- **user_id_fn**：`lambda u: u["sub"]`（Google 以 `sub` 為用戶唯一識別）
- 無 group scopes（Google OAuth 不直接回傳群組）

### Auth0OAuthProvider（providers/auth0_oauth_provider.py）

- **動態端點**：以 `domain` 拼接 `authorization_endpoint` / `token_endpoint` / `userinfo_endpoint`
- **預設 scopes**：`offline_access`（取得 refresh token）
- **額外 user scopes**：`openid`、`profile`、`email`
- **authorization_params**：若提供 `audience`，會加入 `audience` query 參數（用於 API 授權）
- **user_id_fn**：`lambda u: u["sub"]`

### AzureOAuthProvider（providers/azure_oauth_provider.py）

- **動態端點**：以 `tenant` 拼接 v2.0 端點（預設 `common`）
- **User scopes**：`user.read`（Microsoft Graph）
- **User endpoint**：`https://graph.microsoft.com/v1.0/me`
- **user_id_fn**：`lambda u: u["id"]`（Graph 的 `id` 而非 `sub`）
- 儲存 `self.tenant` 供日後參考

---

## URL Launcher

**檔案**：`controls/services/url_launcher.py`

所有服務繼承自 `Service` 基類，並以 `@control("UrlLauncher")` 裝飾。底層透過 `_invoke_method()` 呼叫各平台原生實作。

### 核心方法

| 方法 | 說明 |
|------|------|
| `launch_url(url, mode, ...)` | 開啟 URL（主流方法） |
| `can_launch_url(url)` | 檢查是否有 handler 可處理該 URL |
| `close_in_app_web_view()` | 關閉 App 內嵌 WebView |
| `open_window(url, title, width, height)` | 在 Web 環境開啟彈出視窗 |
| `supports_launch_mode(mode)` | 查詢平台是否支援特定模式 |
| `supports_close_for_launch_mode(mode)` | 查詢某模式是否支援 `close_in_app_web_view()` |

### LaunchMode 列舉

| 成員 | 意義 |
|------|------|
| `PLATFORM_DEFAULT` | 平台自行決定 |
| `IN_APP_WEB_VIEW` | App 內 WebView（行動裝置） |
| `IN_APP_BROWSER_VIEW` | App 內瀏覽器視圖（Custom Tabs） |
| `EXTERNAL_APPLICATION` | 交給外部應用處理 |
| `EXTERNAL_NON_BROWSER_APPLICATION` | 交給非瀏覽器應用處理 |

### 平台限制差異

- **`can_launch_url`**：
  - Android / iOS：新版通常無權查詢，永遠回 `False`
  - Web：只有 `http(s)` 等少數 scheme 會回 `True`（網頁無权查詢已安裝應用）
- **`open_window`**：僅 Web 環境支援（桌面/行動會忽略）
- **`close_in_app_web_view`**：並非所有 launch mode 都支援

---

## Share

**檔案**：`controls/services/share.py`

### 分享類型

| 方法 | 用途 |
|------|------|
| `share_text(text, ...)` | 分享純文字 |
| `share_uri(uri, ...)` | 分享連結 |
| `share_files(files, ...)` | 分享檔案（支援多個） |

### ShareFile 資料類

可從兩種來源建立：
- `ShareFile.from_path(path)`：檔案系統路徑
- `ShareFile.from_bytes(data, mime_type, name)`：記憶體 bytes（跨平台）

建構時 `path` 和 `data` 不可同時為空，否則拋 `ValueError`。

### ShareResult 結果類

```python
@dataclass
class ShareResult:
    status: ShareResultStatus   # SUCCESS / DISMISSED / UNAVAILABLE
    raw: str                   # 平台原始回傳字串
```

### iOS 特殊選項

`excluded_cupertino_activities` 參數可排除特定 iOS activity（如 Facebook、Twitter、AirDrop 等），類型為 `ShareCupertinoActivityType` 列舉。

### 平台通用參數

- `title`：分享 sheet 標題
- `subject`：郵件主旨
- `preview_thumbnail`：分享預覽縮圖
- `share_position_origin`：分享 sheet 彈出位置（Offset）
- `download_fallback_enabled` / `mail_to_fallback_enabled`：下載與 mailto fallback

---

## Clipboard

**檔案**：`controls/services/clipboard.py`

### 方法一覽

| 方法 | 平台限制 | 說明 |
|------|---------|------|
| `set(value: str)` | 無限制 | 寫入字串 |
| `get() -> Optional[str]` | 無限制 | 讀取字串 |
| `set_image(value: bytes)` | Android / iOS / Web | 寫入圖片 bytes |
| `get_image() -> Optional[bytes]` | Android / iOS / Web | 讀取圖片 bytes |
| `set_files(files: list[str])` | Desktop（macOS/Win/Linux） | 寫入檔案參照 |
| `get_files() -> list[str]` | Android / Desktop | 讀取檔案參照 |

### 平台限制實作

```python
# set_image：非 Android/iOS/Web → 拋 FletUnsupportedPlatformException
if not (self.page.web or self.page.platform.is_mobile()):
    raise FletUnsupportedPlatformException("set_image is not supported on this platform")

# set_files：Desktop 限定
if self.page.web or not self.page.platform.is_desktop():
    raise FletUnsupportedPlatformException("set_files is supported on desktop platforms only")

# get_files：Desktop + Android
if self.page.web or (not self.page.platform.is_desktop() and self.page.platform != PagePlatform.ANDROID):
    raise FletUnsupportedPlatformException("get_files is supported on desktop and Android platforms only")
```

### 使用範例

```python
# 複製文字
await page.clipboard.set("Hello")

# 貼上文字
text = await page.clipboard.get()

# 複製圖片（需 mobile 或 web）
await page.clipboard.set_image(image_bytes)
```

---

## 其他 Services

### Service 基類（controls/services/service.py）

```python
@dataclass(kw_only=True)
class Service(BaseControl):
    def init(self):
        super().init()
        context.page._services.register_service(self)  # 自動向 Page 註冊
```

所有 Service 以 `@control("WidgetName")` 裝飾，等同 `@dataclass`。在 `init()` 時自動向 `page._services` 註冊，無需手動实例化。

### SharedPreferences（controls/services/shared_preferences.py）

持久化 Key-Value 儲存（跨工作階段）。

| 方法 | 說明 |
|------|------|
| `set(key, value) -> bool` | 寫入（value 不可為 None） |
| `get(key)` | 讀取 |
| `contains_key(key) -> bool` | 鍵是否存在 |
| `remove(key) -> bool` | 刪除單一鍵 |
| `get_keys(key_prefix) -> list[str]` | 前綴查詢所有鍵 |
| `clear() -> bool` | 清除所有 |

### StoragePaths（controls/services/storage_paths.py）

取得各平台標準目錄路徑。**Web 模式全部不支援**，會拋 `FletUnsupportedPlatformException`。

| 方法 | 平台限制 | 說明 |
|------|---------|------|
| `get_application_cache_directory()` | 非 Web | 應用快取目錄 |
| `get_application_documents_directory()` | 非 Web | 使用者文件目錄 |
| `get_application_support_directory()` | 非 Web | 應用支援檔案目錄 |
| `get_temporary_directory()` | 非 Web | 暫存目錄 |
| `get_library_directory()` | Apple 限定 | 程式庫目錄（備份用） |
| `get_downloads_directory()` | 非 Web | 下載目錄 |
| `get_external_storage_directory()` | Android | 外部儲存根目錄 |
| `get_external_cache_directories()` | Android | 外部快取目錄（SD 卡） |
| `get_external_storage_directories()` | Android | 外部儲存目錄 |
| `get_console_log_filename()` | 非 Web | 主控台日誌檔路徑 |

### Battery（controls/services/battery.py）

| 方法 | 說明 |
|------|------|
| `get_battery_level() -> Optional[int]` | 電量百分比（0–100），`None` 表示無法取得 |
| `get_battery_state() -> BatteryState` | 當前狀態（CHARGING / DISCHARGING / FULL 等） |
| `is_in_battery_save_mode() -> bool` | 是否在省電模式 |

支援事件：`on_state_change`（電量狀態改變時觸發）。

---

## 重要發現與注意事項

### Auth 系統

1. **PKCE 支援完整**：Provider 可傳入 `code_challenge` + `code_challenge_method` + `code_verifier`，適用於公開客戶端（如 SPA、行動 App）。
2. **Token 刷新時不覆蓋 refresh_token**：若 provider 回應未帶 `refresh_token`，保留舊的（避免被覆蓋為 `None`）。
3. **User 是 dict 擴展**：可直接用 `user["email"]`、`user["name"]` 等 provider 原生欄位。
4. **Provider 雙層抓取策略**：優先用 `provider._fetch_user()`（特化 API），失敗才走通用 `user_endpoint` + `user_id_fn`。
5. **Scope 自動合併**：Constructor 會把 `provider.scopes`、`user_scopes`、`group_scopes` 全部合併進 `self.scope`。
6. **GitHub 的 email 特殊處理**：需二次請求 `/user/emails` 才能取得 primary email（第 55–69 行）。
7. **Azure vs Google 的 user_id**：Azure 用 Graph 的 `id`，Google 用 OIDC 的 `sub`。

### URL Launcher

1. **`can_launch_url` 在行動裝置永遠回 False**：因隱私限制，App 無權查詢系統。
2. **`open_window` 僅 Web 有意義**：其他平台會忽略。
3. **關閉 WebView 不是所有模式都支援**：需先 `supports_close_for_launch_mode()` 確認。

### Share

1. **分享檔案兩種來源**：`from_path()`（磁碟檔案）或 `from_bytes()`（記憶體），平台底層自動處理。
2. **iOS 排除 activity**：可用 `excluded_cupertino_activities` 排除特定分享目標。
3. **`share_text` 和 `share_uri` 是分開的方法**：URI 分享不走 `share_text`。

### Clipboard

1. **圖片讀寫僅支援 Mobile + Web**：Desktop 不支援，會拋例外。
2. **檔案參照讀寫僅支援 Desktop + Android**：Web 完全不支援。
3. **`set_files` 的 Android 回傳內容**：通常是 content URI 而非路徑。

### Service 通用

1. **所有 Service 自動向 Page 註冊**：在 `init()` 階段完成，無需手動管理生命週期。
2. **底層都是 `_invoke_method` 呼叫平台實作**：Python 端純為介面包裝，真正的實作在 Dart/Flet SDK。
3. **沒有獨立的 Permissions Service**：Flet 0.82.2 的 `permissions` 功能未包裝為獨立 Service（權限請求通常在平台層處理，或透過特定 Control 觸發）。
