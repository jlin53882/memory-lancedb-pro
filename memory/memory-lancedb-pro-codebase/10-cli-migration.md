# memory-lancedb-pro CLI、遷移、壓實與附加工具分析報告

> 分析目標：深度分析 memory-lancedb-pro 的 CLI 介面、資料庫遷移、記憶體壓實、記憶升級與 OAuth 流程

## 一、CLI 介面分析（cli.ts）

### 1.1 命令結構總覽

CLI 採用 Commander.js 框架，以 `memory-pro` 為主命令，提供以下子命令群組：

```
memory-pro
├── version                 # 顯示插件版本
├── auth                   # OAuth 認證管理
│   ├── login              # OAuth 登入（瀏覽器認證）
│   ├── status             # 顯示當前 OAuth 狀態
│   └── logout             # 登出並還原 API Key 模式
├── list                   # 列出記憶體（支援 scope/category 過濾）
├── search <query>         # 混合檢索（向量 + BM25）
├── stats                  # 顯示統計資訊
├── delete <id>            # 刪除單一記憶體
├── delete-bulk            # 大量刪除（按 scope/日期）
├── export                 # 匯出為 JSON
├── import <file>          # 從 JSON 匯入
├── import-markdown        # 從 Markdown 檔案匯入（MEMORY.md）
├── reembed                # 重新向量化的遷移工具
├── upgrade                # 升級舊格式記憶體
└── migrate                # 遷移工具群
    ├── check              # 檢查是否需要遷移
    ├── run                # 執行遷移
    └── verify             # 驗證遷移結果
```

### 1.2 核心功能說明

#### 1.2.1 OAuth 認證管理（auth）

- **login**：開啟瀏覽器進行 ChatGPT/Codex OAuth 認證，自動更新 `openclaw.json` 配置
- **status**：顯示當前 OAuth 配置、供應商、模型、token 檔案狀態
- **logout**：刪除 OAuth 檔案，還原為 API Key 模式

OAuth 流程特色：
- 支援 PKCE（Proof Key for Code Exchange）安全機制
- 自動備份既有 LLM 配置（API Key、baseURL 等）
- 支援多供應商（目前僅 OpenAI Codex）
- 互動式供應商選擇（TUI 選單）

#### 1.2.2 檢索功能（search）

- 預設使用混合檢索（向量 + BM25 + Rerank）
- 支援 scope 與 category 過濾
- 顯示來源與相關性分數（向量/BM25/reranked）

#### 1.2.3 匯入匯出

- **import**：從 JSON 匯入，支援冪等性（id 重複則跳過）+ 相似度去重
- **import-markdown**：從 workspace 的 MEMORY.md 和 memory/YYYY-MM-DD.md 匯入
- **export**：匯出為 JSON，排除向量以減少檔案大小

#### 1.2.4 Re-embed 功能

用於 A/B 測試不同 embedding 模型：
- 從來源 LanceDB 讀取所有記憶體
- 使用當前配置的 embedder 重新向量
- 寫入目標資料庫
- 支援批次處理、dry-run、skip-existing

---

## 二、資料庫遷移分析（migrate.ts）

### 2.1 版本管理策略

遷移模組採用**向前相容策略**：
- 來源：舊版 `memory-lancedb` 插件的 LanceDB 資料庫
- 目標：新版 `memory-lancedb-pro` 的增強 schema

不採用傳統的版本號機制，而是透過**自動偵測**與**欄位對照**完成遷移。

### 2.2 Schema 變更處理

#### 舊版格式（LegacyMemoryEntry）

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | string | 記憶體 ID |
| text | string | 內文 |
| vector | number[] | 向量 |
| importance | number | 重要性（0-1）|
| category | 5-category | preference/fact/decision/entity/other |
| createdAt | number | 時間戳 |
| scope | string? | 作用域 |

#### 新版格式（MemoryEntry）

除上述欄位外，新增：
- **metadata**：JSON 字串，可存放遷移元數據（`migratedFrom: "memory-lancedb"`）

### 2.3 遷移流程

```
1. findSourceDatabase()
   - 檢查預設路徑：~/.openclaw/memory/lancedb, ~/.claude/memory/lancedb
   - 支援 explicit path 覆寫

2. loadLegacyData()
   - 連接舊版 LanceDB
   - 開啟 "memories" 表
   - 向量正規化（處理不同格式）

3. migrateEntries()
   - 若啟用 skipExisting：檢查 id 存在或相似度 > 0.95
   - 轉換格式並標記元數據
   - 批次寫入目標 store

4. verifyMigration()
   - 比對來源與目標的記憶體數量
   - 檢查數量一致性
```

### 2.4 特殊設計

- **向量正規化**（normalizeLegacyVector）：處理舊版可能儲存的各種向量格式
- **冪等性支援**：dry-run 模式、skip-existing 選項
- **自動路徑偵測**：檢查 `.lance` 副檔名或 `memories.lance` 檔案

---

## 三、記憶體壓實分析（memory-compactor.ts）

### 3.1 觸發條件

壓實（Compaction）可在以下情境觸發：

| 條件 | 預設值 | 說明 |
|------|--------|------|
| `minAgeDays` | 7 | 只處理 N 天前的記憶體 |
| `minClusterSize` | 2 | 最少 2 個記憶體形成叢集才觸發 |
| `similarityThreshold` | 0.88 | Cosine similarity 閾值 |
| `cooldownHours` | 24 | 執行間隔（避免頻繁壓實）|

### 3.2 摘要演算法（漸進摘要）

#### Step 1：叢集建構（Greedy Clustering）

```
1. 按 importance 降序排列所有記憶體
2. 取最高重要性的未分配記憶體作為 seed
3. 將 cosine similarity >= threshold 的未分配記憶體加入叢集
4. 重複直到所有記憶體分配完畢
5. 篩選 cluster.length >= minClusterSize
```

#### Step 2：合併策略

針對每個符合條件的叢集：

| 欄位 | 合併策略 |
|------|----------|
| **text** | 行層級去重（trim + lowercase 比較）|
| **importance** | 取最大值（never downgrade）|
| **category** | 多數投票（plurality vote）|
| **scope** | 必須全部相同 |
| **metadata** | 標記 `{ compacted: true, sourceCount: N }` |

#### Step 3：向量重新計算

合併後的記憶體需重新 embedding（使用 `embedder.embedPassage`）。

### 3.3 數學工具

- **cosineSimilarity**：計算向量相似度，避免 NaN（任一向量 norm 為 0 時回傳 0）
- **dot product** + **L2 norm**：標準向量運算

### 3.4 執行模式

- **dry-run**：僅報告掃描數與叢集數，不寫入
- **cooldown**：透過 JSON 檔案紀錄 lastRunAt，確保間隔時間

---

## 四、記憶升級分析（memory-upgrader.ts）

### 4.1 升級目標

將舊版 5-category 格式升級為新版 6-category + L0/L1/L2 智慧格式：

| 舊版 category | 新版 memory_category |
|---------------|---------------------|
| preference | preferences |
| entity | entities |
| decision | events |
| other | patterns |
| fact | **profile** 或 **cases**（需 LLM 判斷）|

### 4.2 升級流程

```
1. isLegacyMemory()
   - 檢查 metadata 是否存在
   - 解析 JSON，確認是否有 memory_category 欄位
   - 若無 → 判定為 legacy

2. countLegacy()
   - 掃描所有記憶體，統計需升級的數量
   - 按 category 分組統計

3. upgrade() [主流程]
   - 分批處理（預設 batchSize: 10）
   - 對每個 legacy entry：
     a. reverseMapCategory()：5-category → 6-category
     b. 生成 L0/L1/L2（LLM 或 fallback）
     c. 寫入新 metadata
```

### 4.3 L0/L1/L2 生成策略

#### 有 LLM 時

```prompt
Given a raw memory text and its category, produce a structured 3-layer summary.

**Category**: {category}

**Raw memory text**:
"""
{text}
"""

Return ONLY valid JSON:
{
  "l0_abstract": "One sentence (≤30 words)",
  "l1_overview": "Markdown bullet points",
  "l2_content": "Full original text",
  "resolved_category": "resolved category if ambiguous"
}
```

#### 無 LLM 時（fallback）

- **L0**：取第一句話（最多 100 字元）
- **L1**：格式化為單一 bullet point
- **L2**：原始文字

### 4.4 特殊處理

- **fact → profile/cases** 模糊判斷：
  - 文本小於 200 字元且含 "my | i am | 我是" 等個人身份關鍵字 → profile
  - 否則 → cases
- **confidence**：預設 0.7
- **tier**：預設 "working"
- **access_count**：預設 0（後續由 access-tracker 更新）

---

## 五、LLM OAuth 流程分析（llm-oauth.ts）

### 5.1 OAuth 供應商

目前僅支援 **OpenAI Codex**：

| 設定 | 值 |
|------|-----|
| authorizeUrl | https://auth.openai.com/oauth/authorize |
| tokenUrl | https://auth.openai.com/oauth/token |
| clientId | app_EMoamEEZ73f0CkXaXp7hrann |
| redirectUri | http://localhost:1455/auth/callback |
| scope | openid profile email offline_access |

### 5.2 認證流程（PKCE）

```
1. createPkceVerifier()    → 32 bytes random, base64url
2. createPkceChallenge()   → SHA256(verifier) → base64url
3. createState()           → 16 bytes random, hex
4. buildAuthorizationUrl() → 組合所有參數（含 PKCE + extra params）
5. performOAuthLogin()
   ├── 開啟瀏覽器（或自訂 onOpenUrl）
   ├── waitForAuthorizationCode() → 本機 HTTP server 等待 callback
   ├── exchangeAuthorizationCode() → 兌換 access token
   └── saveOAuthSession() → 寫入 JSON 檔案
```

### 5.3 Token 管理

- **loadOAuthSession()**：從 JSON 檔案讀取並解析
- **refreshOAuthSession()**：使用 refresh_token 刷新
- **needsRefresh()**：檢查是否過期（預留 60 秒 skew）

### 5.4 Session 結構

```typescript
interface OAuthSession {
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;      // JWT exp 或 expires_in 計算
  accountId: string;      // ChatGPT account id
  providerId: "openai-codex";
  authPath: string;       // oauth.json 檔案路徑
}
```

### 5.5 安全性設計

- **PKCE**：防止 authorization code 攔截攻擊
- **Scopes**：要求 offline_access 以支援 refresh
- **local redirect**：localhost callback，無需公開端點
- **state 驗證**：防止 CSRF

---

## 六、總結與架構洞察

### 6.1 設計模式

| 模組 | 模式 | 說明 |
|------|------|------|
| CLI | Command + Factory | Commander.js 子命令註冊，createMemoryCLI factory |
| Migration | Observer/Adapter | 舊版 → 新版 adapter，自動路徑偵測 |
| Compactor | Greedy Clustering | 重要性排序的貪心叢集擴展 |
| Upgrader | Pipeline | 檢測 → 分類 → 摘要 → 寫入 |
| OAuth | State Machine | 登入 → 回调 → 兌換 → 儲存 |

### 6.2 可擴展性

- **CLI**：支援自訂 embedder/llmClient/retriever 注入
- **Compactor**：Duck-typed store interface，可替換後端
- **Upgrader**：支援 LLM fallback，無外部依賴仍可運作
- **OAuth**：Provider 定義外部化，新增供應商只需擴展 OAUTH_PROVIDERS

### 6.3 風險與限制

1. **Compactor**：相似度閾值 0.88 可能需調優；去重僅限行層級
2. **Upgrader**：無 LLM 時的 fallback 品質較低
3. **OAuth**：僅支援單一供應商（OpenAI Codex）
4. **Migration**：舊版向量格式多樣，依賴 normalizeLegacyVector 處理

---

*報告產生時間：2026-04-02*
*分析目標版本：memory-lancedb-pro (latest)*