# Claude Code CLI Skill 系統深度分析

> 分析日期：2026-04-02
> 來源：Claude Code CLI 洩漏原始碼（https://github.com/win4r/claude-code-2）

## 一、Skill 架構全景圖

```
Skill 來源（5+1 種）
├─ bundled   → 程式化註冊，內建於 CLI 二進位
├─ managed   → ~/.claude/skills/（政策管理）
├─ user      → ~/.claude/skills/（使用者）
├─ project   → .claude/skills/（專案）
├─ commands_DEPRECATED → commands/（舊格式向後相容）
├─ mcp       → MCP server 動態發現
└─ 動態發現  → 編輯時即時發現巢狀 .claude/skills/
        │
        ▼
   統一轉換為 Command 物件（PromptCommand / LocalCommand / LocalJSXCommand）
        │
        ▼
   SkillTool 統一調用
        │
        ▼
   兩種執行模式：inline（對話內展開）←→ fork（子 Agent 隔離執行）
```

---

## 二、Skill 定義格式

### 2.1 磁碟格式：SKILL.md + YAML Frontmatter

```markdown
---
name: 顯示名稱
description: 單行描述（必要）
allowed-tools:        # Tool 權限白名單（正規表達式）
  - Read
  - Grep
  - Bash(npm:*)
when_to_use: 詳細使用時機說明
argument-hint: "<instruction>"
arguments:
  - instruction
context: fork        # inline（預設）或 fork
agent: general-purpose  # fork 時使用的 Agent 類型
model: opus          # 可指定模型
effort: medium       # effort 等級
user-invocable: true # 是否可被用戶直接呼叫
disable-model-invocation: false
paths:               # 條件觸發：匹配的檔案被觸碰才啟用
  - "src/**/*.ts"
  - "*.config.js"
hooks:
  pre-invoke:
    - type: log
      message: "Skill starting"
---
# Skill 內容本體（Markdown）
```

### 2.2 核心資料結構：PromptCommand

```typescript
type PromptCommand = {
  type: 'prompt'
  name: string
  description: string
  argNames?: string[]
  allowedTools?: string[]       // Tool 白名單
  model?: string              // 模型覆寫
  effort?: EffortValue
  source: SettingSource | 'bundled' | 'mcp' | 'plugin'
  loadedFrom: 'commands_DEPRECATED' | 'skills' | 'plugin' | 'managed' | 'bundled' | 'mcp'
  hooks?: HooksSettings
  skillRoot?: string
  context?: 'inline' | 'fork'
  agent?: string
  paths?: string[]              // 條件路徑匹配
  isEnabled?: () => boolean
  isHidden?: boolean
  userInvocable?: boolean
  getPromptForCommand(args: string, context: ToolUseContext): Promise<ContentBlockParam[]>
}
```

---

## 三、Skill 生命週期

### 3.1 註冊 → 發現 → 載入

```
啟動時：
  1. initBundledSkills() → registerBundledSkill()
  2. getSkillDirCommands(cwd) [memoized]
       ├── loadSkillsFromSkillsDir() → 遞迴每個 skill-name/SKILL.md
       ├── loadSkillsFromCommandsDir() → 舊格式向後相容
       └── MCP skills 動態發現
  3. 去重：realpath() 比對
  4. 分離 conditional skills（paths frontmatter）

編輯時動態發現（discoverSkillDirsForPaths）：
  - 監聽檔案路徑變更，從檔案所在目錄向上 walk
  - 找到 .claude/skills/ 就 loadSkillsFromSkillsDir()
  - 觸發 skillsLoaded Signal → 清除快取
```

### 3.2 執行模型：Inline vs Fork

| 維度 | Inline | Fork |
|------|--------|------|
| 執行位置 | 當前對話 | 隔離子 Agent |
| Token 預算 | 共享對話預算 | 獨立子 Agent 預算 |
| 觸發方式 | `context: inline`（預設）| `context: fork` |
| 適用情境 | 小型、需引用對話歷史 | 大型、自成體系的工作流 |

### 3.3 權限模型

```typescript
// 兩層安全：
// 1. 靜態檢查：skillHasOnlySafeProperties() — 只含白名單屬性則自動允許
// 2. 動態詢問：否則 Suggest allow rule 並請求用戶確認

// Tool 權限傳遞：
// skill.allowedTools → alwaysAllowRules.command[] → toolPermissionContext
```

---

## 四、工具整合

### SkillTool 統一入口

```
輸入：{ skill: "batch", args: "migrate from foo to bar" }
輸出（inline）：{ success: true, newMessages: [...], contextModifier: {...} }
輸出（fork）：  { success: true, status: "forked", agentId: "...", result: "..." }
```

### MCP 整合

MCP Server 連接時，技能透過 `mcpSkillBuilders` 間接依賴（寫時註冊模式）：
```typescript
registerMCPSkillBuilders({ createSkillCommand, parseSkillFrontmatterFields })
```

---

## 五、可借鑒的設計

### 1. Conditional Skills（路徑條件觸發）

```typescript
// Skill 在 frontmatter 宣告 paths，只有 matching 檔案被觸碰才激活
// 用 ignore() 庫實現 gitignore 語義匹配
// 節省 token：路徑不符的 Skill 一開始就不暴露給模型
```

### 2. 動態 Skill 目錄發現

```typescript
// 編輯時自動向上 walk 找到巢狀 .claude/skills/
// 無需重啟，即時發現新 Skill
discoverSkillDirsForPaths() + addSkillDirectories()
```

### 3. Bundled Skill 的參考檔案提取

```typescript
// Bundled Skill 可附帶 files{}，首次執行時提取到磁碟
// 讓模型可以 Read/Grep 這些檔案
// ${CLAUDE_SKILL_DIR} 替換成實際路徑
```

### 4. Skill 的 Fork 隔離執行

```typescript
// context: fork → 完全隔離的子 Agent，獨立 token 預算
// 適用於大型破壞性工作流（batch 模式），不影響主對話狀態
```

---

## 六、與 OpenClaw 現有 Skill 系統差異

| 面向 | Claude Code CLI | OpenClaw 現況 |
|------|----------------|--------------|
| **定義格式** | SKILL.md + 標準化 YAML frontmatter，有完整 schema | SKILL.md，無強制 frontmatter 格式 |
| **發現機制** | 5+1 種來源，含動態發現 | 目錄掃描，無動態發現 |
| **條件觸發** | `paths` frontmatter + ignore() 庫匹配 | 無此機制 |
| **執行模型** | inline/fork 雙模式，fork 有獨立 Agent 預算 | 單一執行，無隔離子 Agent |
| **Tool 權限** | `allowed-tools` frontmatter → alwaysAllowRules | 多數 Tool 全域開通，無聲明式 Tool 權限 |
| **參考檔案** | Bundled Skill 可附帶 `files{}` 提取到磁碟 | 無此機制 |
| **參數支援** | `arguments` + `argument-hint` + `$ARG` 插值 | 依賴 prompt 內文字替換 |
| **Hook 系統** | `hooks: { pre-invoke, post-invoke }` | 無 Hook 系統 |
| **MCP 整合** | MCP Skill 統一 discovery | MCP 是獨立的 Tool，不是 Skill |
