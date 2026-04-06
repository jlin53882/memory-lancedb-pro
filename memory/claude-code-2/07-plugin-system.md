# Claude Code CLI Plugin 系統深度分析報告

> 分析日期：2026-04-02
> 來源：Claude Code CLI 洩漏原始碼（https://github.com/win4r/claude-code-2）

## 一、Plugin 系統架構

### 1.1 Plugin Manifest 格式（plugin.json）

Claude Code 使用 `plugin.json` 作為 Plugin 的定義檔案，主要結構如下：

```typescript
// 核心 Schema（schemas.ts）
{
  name: string,           // Plugin 名稱（kebab-case）
  version?: string,       // Semantic version
  description?: string,   // 描述
  author?: { name, email, url },
  dependencies?: string[], // 依賴的其他 plugins
  commands?: string | string[] | { [name]: CommandMetadata },
  agents?: string | string[],
  skills?: string | string[],
  hooks?: HooksSettings | string,
  mcpServers?: McpServerConfig | string | .mcpb file,
  lspServers?: LspServerConfig,
}
```

**Plugin ID 格式**：`name@marketplace`（例如 `my-plugin@official`）

### 1.2 兩種 Plugin 類型

| 類型 | 來源 | 啟用方式 |
|------|------|----------|
| **Built-in** | 內建於 CLI (`src/plugins/bundled/`) | 使用者可透過 `/plugin` UI 開關 |
| **Marketplace** | 外部 marketplace 或 GitHub | 安裝後由 `enabledPlugins` 控制 |

---

## 二、Plugin 載入和初始化流程

### 2.1 核心載入流程（pluginLoader.ts）

```
loadAllPlugins()
  ├── loadPluginsFromMarketplaces()
  │   ├── 讀取用戶 settings 中的 enabledPlugins
  │   ├── 驗證 enterprise policy（allowlist/blocklist）
  │   ├── 預載入 marketplace catalogs
  │   └── 並行載入每個 plugin
  │
  └── loadPluginFromMarketplaceEntry()
      ├── 根據 source 類型選擇安裝方式：
      │   ├── local: 從 marketplace 目錄复制
      │   ├── github: git clone
      │   ├── npm: npm install
      │   ├── git-subdir: sparse-checkout
      │   └── url: 下載並解壓
      │
      ├── copyPluginToVersionedCache() → 版本化快取
      │   └── ~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/
      │
      └── finishLoadingPluginFromPath()
          ├── loadPluginManifest() → 驗證 plugin.json
          ├── loadPluginHooks() → hooks/hooks.json
          ├── loadPluginSettings() → plugin-specific 設定
          └── 處理額外的 commands/agents/skills 路徑
```

### 2.2 版本化快取機制

Claude Code 使用**版本化快取**避免升級破壞：
- 路徑格式：`~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/`
- 支援 ZIP 快取（`isPluginZipCacheEnabled()`）
- Seed 目錄預先填充 plugin

### 2.3 Hooks 生命週期（loadPluginHooks.ts）

```typescript
loadPluginHooks() // memoized
  → loadAllPluginsCacheOnly()
  → 轉換 hooks 為 PluginHookMatcher[]
  → clearRegisteredPluginHooks()
  → registerHookCallbacks(allPluginHooks)
```

**Hooks 事件類型**：
- `PreToolUse` / `PostToolUse` / `PostToolUseFailure`
- `PermissionDenied` / `PermissionRequest`
- `SessionStart` / `SessionEnd`
- `Notification` / `UserPromptSubmit`
- `PreCompact` / `PostCompact`
- `SubagentStart` / `SubagentStop`
- `ConfigChange` / `FileChanged` 等

---

## 三、Plugin 與內建 Tools/Commands 的整合方式

### 3.1 Commands 載入（loadPluginCommands.ts）

Plugin 的 commands 來自：
1. **標準目錄**：`commands/*.md`
2. **Manifest 擴展**：`manifest.commands` 指定額外路徑
3. **Skill 目錄**：`skills/*/SKILL.md`

```typescript
// 命名空間機制
getCommandNameFromFile()
  // 檔案：my-plugin/commands/build.md → /plugin:build
  // Skill：my-plugin/skills/docker/build.md → /plugin:docker:build
```

### 3.2 Hooks 整合

Plugin 可提供 hooks（攔截點），與核心深度整合：
- 每個 hook 帶有 `pluginRoot`, `pluginName`, `pluginId`
- 支援變數替換（`substitutePluginVariables`）
- 支援使用者設定（`userConfig`）

### 3.3 MCP/LSP 整合

Plugin 可附帶：
- **MCP Servers**：自動配置 `.mcp.json`
- **LSP Servers**：語言伺服器配置
- 支援 `.mcpb`（MCP Bundle）格式

---

## 四、Plugin 的安全隔離機制

### ⚠️ 關鍵發現：無隔離機制

Claude Code Plugin 系統**目前沒有 VM sandbox、process isolation 或權限控制**：
- Plugin 代碼與核心**共享同一程序**
- 可直接存取 filesystem、environment variables
- Hooks 可監聽所有事件（`PreToolUse` 可修改 tool 輸入）

**安全機制僅限於**：
1. **Enterprise Policy**：允許/封鎖 marketplace
2. **Manifest 驗證**：Zod schema 驗證格式
3. **名稱保護**：阻止冒充官方 marketplace（`claude-code-*`, `anthropic-*`）

---

## 五、可借鑒到 OpenClaw 的設計

### 5.1 值得採用的設計

| 特性 | 價值 | 建議 |
|------|------|------|
| **版本化快取** | 防止升級破壞、支援 rollback | OpenClaw 可採用 |
| **Manifest Schema 驗證** | 類型安全、early error | 用 Zod 驗證 |
| **Hooks 系統** | 深度擴展性 | OpenClaw 已有類似設計 |
| **依賴解析** | `dependencies` 欄位管理依賴 | 可考慮 |
| **Seed 目錄** | BYOC（Bring Your Own Plugin）| 可預填充 plugin |

### 5.2 應避免的設計

| 問題 | 原因 |
|------|------|
| **無隔離** | Plugin 可執行任意代碼，風險極高 |
| **共享程序** | Plugin crash 可能影響主程序 |
| **依賴外部網路** | 啟動時需要網路 clone |

---

## 六、與 OpenClaw 現有 Plugin 系統的差異

### 6.1 架構對比

| 面向 | Claude Code | OpenClaw |
|------|-------------|----------|
| **Manifest** | `plugin.json`（JSON） | `SKILL.md`（Markdown） |
| **Plugin ID** | `name@marketplace` | Skill 目錄結構 |
| **依賴管理** | manifest.dependencies | 無（手動管理） |
| **快取機制** | 版本化 ZIP cache | 未版本化 |
| **Hooks** | 完整事件監聽 | 部分相似 |
| **隔離** | ❌ 無 | ⚠️ 需確認 |

### 6.2 關鍵差異

1. **Manifest 格式**：Claude Code 用 JSON Schema + Zod，OpenClaw 用 Markdown frontmatter
2. **命名空間**：`plugin:name:command` vs OpenClaw 的 skill 目錄
3. **Plugin 來源**：集中式 marketplace vs 目錄/ClawHub
4. **安全模型**：Claude Code 無隔離，OpenClaw 需評估

### 6.3 建議改進

- 為 OpenClaw 引入**版本化快取**機制
- 參考 Claude Code 的 **Hooks 類型定義**（更完整的事件類型）
- 考慮引入 **Plugin Schema 驗證**（目前依賴 Markdown）
- **評估安全隔離需求**（如需隔離，考慮 worker threads 或 isolates）
