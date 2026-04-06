# Claude Code 2 Token 成本追蹤系統深度分析

> 分析目標 Repo：https://github.com/win4r/claude-code-2
> 分析日期：2026-04-02

---

## 一、成本追蹤架構

### 1.1 核心模組 `cost-tracker.ts`

Claude Code 2 的成本追蹤採用**三層架構**：

| 層級 | 檔案 |職責 |
|------|------|-----|
| **State 層** | `bootstrap/state.ts` | 全域狀態儲存（totalCostUSD, modelUsage 等）|
| **Tracker 層** | `cost-tracker.ts` | 成本計算、格式化、專案設定持久化 |
| **Presentation 層** | CLI 輸出 | 使用 Chalk 彩色輸出 |

**關鍵 State 欄位**：
```typescript
totalCostUSD: number
totalAPIDuration: number
totalToolDuration: number
totalLinesAdded/Removed: number
modelUsage: { [modelName: string]: ModelUsage }
```

### 1.2 Cost Breakdown by Tool/Call

Claude Code 2 在每次 API 請求後記錄詳細使用量：

```typescript
// cost-tracker.ts: addToTotalSessionCost()
addToTotalModelUsage(cost, usage, model)  // 按模型累加
getCostCounter()?.add(cost, attrs)         // OpenTelemetry 遙測
getTokenCounter()?.add(input_tokens, {...attrs, type: 'input'})
getTokenCounter()?.add(output_tokens, {...attrs, type: 'output'})
```

**屬性追蹤**：
- `model`: 模型名稱
- `speed`: fast mode 標記
- `type`: input/output/cacheRead/cacheCreation

### 1.3 成本儲存與恢復機制

```typescript
// 儲存到專案設定 (.claude/settings.json)
saveCurrentSessionCosts(fpsMetrics)

// 恢復機制
restoreCostStateForSession(sessionId)
getStoredSessionCosts(sessionId)
```

**特點**：Session 結束時寫入，下次啟動同名資料夾時自動恢復。

---

## 二、Token 估算邏輯

### 2.1 多層估算策略

| 方法 | 精確度 | 適用場景 |
|------|--------|---------|
| `countTokensWithAPI()` | 最高 | API 可用時（預設）|
| `countTokensViaHaikuFallback()` | 高 | API 失敗時，使用 Haiku 模型估算 |
| `roughTokenCountEstimation()` | 低 | 後備 fallback |

### 2.2 API Token Count

```typescript
// tokenEstimation.ts: countMessagesTokensWithAPI()
const response = await anthropic.beta.messages.countToken({
  model, messages, tools, betas,
  thinking: { type: 'enabled', budget_tokens: 1024 }
})
return response.input_tokens
```

**支援**：Bedrock、Vertex、普通 API 三種 Provider。

### 2.3 Rough Estimation 演算法

```typescript
// 基礎公式：content.length / bytesPerToken
roughTokenCountEstimation(content, bytesPerToken = 4)

// 檔案類型優化
bytesPerTokenForFileType(ext) {
  case 'json': return 2   // JSON 更密集
  default: return 4
}
```

**圖片 token 估算**：
```typescript
// Images: (width * height) / 750
// 上限：2000 tokens（Resize to 2000x2000）
```

### 2.4 Context 壓縮中的 Token 管理

**microCompact.ts** 核心機制：

```typescript
// 估算訊息 token 數量
estimateMessageTokens(messages) {
  // 對各 block 類型分別估算
  - text: roughTokenCountEstimation(block.text)
  - tool_result: calculateToolResultTokens(block)
  - image/document: IMAGE_MAX_TOKEN_SIZE (2000)
  - thinking: roughTokenCountEstimation(block.thinking)
  
  // 保守估計：乘以 4/3
  return Math.ceil(totalTokens * (4 / 3))
}
```

**兩種觸發模式**：
1. **Time-based MC**：閒置超過 N 分鐘 → 清除舊 tool results
2. **Cached MC**：使用 cache_edits API 編輯快取，不修改本地訊息

---

## 三、成本上限控制

### 3.1 Context Window 控制

```typescript
getContextWindowForModel(model, betas)
getModelMaxOutputTokens(model).default
```

### 3.2 估算觸發壓縮

當 `estimateMessageTokens()` 接近 context window 時觸發 auto-compact。

---

## 四、可借鑒到 OpenClaw 的設計

### 4.1 值得移植的功能

| 功能 | Claude Code 做法 | OpenClaw 現況 | 建議 |
|------|-----------------|--------------|------|
| **Session 成本恢復** | 寫入 settings.json | 無 | 可實現 |
| **Model 分項統計** | modelUsage map | 僅 total | 擴充 |
| **Token Counter 遙測** | OpenTelemetry | 無 | 可整合 |
| **多 Provider 估算** | API/Bedrock/Vertex | 僅 API | 擴充 |
| **Rough Estimation** | bytesPerToken 優化 | 無 | 可參考 |

### 4.2 具體建議

1. **cost-tracker 模組化**：將成本追蹤從 state.ts 抽離為獨立模組
2. **tokenEstimation 分層**：實作 API count → Haiku fallback → rough estimation 三層 fallback
3. **專案設定持久化**：參考 `saveCurrentSessionCosts()` 機制
4. **microCompact 借鑒**：Context 壓縮時使用保守估算（×4/3）

---

## 五、與 OpenClaw 現有成本管理的差異

| 面向 | Claude Code 2 | OpenClaw |
|------|-------------|----------|
| **Token 估算** | 多層策略（API/Haiku/rough）| 依賴 API 回傳 |
| **成本儲存** | 寫入專案設定，Session 恢復 | 無持久化 |
| **Model 追蹤** | 按模型分別統計 | 統一總量 |
| **Tool 遙測** | OpenTelemetry counter | 無 |
| **Context 壓縮** | Cached MC + Time-based MC | 基本壓縮 |
| **圖片估算** | 固定 2000 tokens | 可能無 |

---

## 六、程式碼位置對照

| 功能 | Claude Code 2 路徑 |
|------|-------------------|
| 成本追蹤核心 | `src/cost-tracker.ts` |
| Token 估算 | `src/services/tokenEstimation.ts` |
| 狀態管理 | `src/bootstrap/state.ts` |
| Context 壓縮 | `src/services/compact/microCompact.ts` |
| 模型成本計算 | `src/utils/modelCost.ts` |

---

*本分析報告由 Subagent 產生，目標為提供 OpenClaw 成本管理系統改進參考。*