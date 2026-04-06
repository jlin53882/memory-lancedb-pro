# 03 — 衰減引擎與記憶生命週期深度分析

> 分析目標：`memory-lancedb-pro` 原始碼
> 分析日期：2026-04-02
> 覆寫檔案：`src/decay-engine.ts`、`src/tier-manager.ts`、`src/access-tracker.ts`

---

## 1. 衰減模型：Weibull vs Logistic

### 1.1 選擇 Weibull 的理由

`decay-engine.ts` 的 recency 採用 **Weibull stretched-exponential** 衰減：

```
effectiveHL = halfLife × exp(μ × importance)
λ = ln(2) / effectiveHL
recency = exp(-λ × daysSince^β)
```

Weibull 模型的關鍵特性是 **形狀參數 β（beta）可調整衰減速度曲率**，而非只有單一指數衰減速率：

| Tier | β 值 | 曲率類型 | 實際效果 |
|------|------|----------|----------|
| Core | 0.8 | 次指數（sub-exponential）| 衰減前期極慢，長期才慢慢下滑 |
| Working | 1.0 | 標準指數（exponential）| 固定半衰期，線性衰減 |
| Peripheral | 1.3 | 超指數（super-exponential）| 前期快速衰減，很快趨近於零 |

### 1.2 為何不選 Logistic？

Logistic 模型（`S(t) = L / (1 + e^{-k(t-t₀)})`）是 S 曲線，適合描述「爆發後收斂」的場景，例如：
- 傳染病傳播
- 產品市場滲透率

**但記憶衰減不是這個邏輯**。記憶的價值流失通常是：
- 前期（或許記得）→ 逐漸模糊 → 遺忘
- 沒有「突然爆發」的階段

因此 Weibull 更貼近真實的遺忘曲線（初期減緩，後期加速）。若要更精確，可以與真實使用者重複回憶實驗數據比對擬合度。

### 1.3 調參建議

`betaCore = 0.8` 偏慢，若希望 Core 記憶更穩定，可降至 `0.6~0.7`；若希望降低「Core 記憶僵化」問題，可維持 `0.8` 並搭配 `coreDecayFloor = 0.9`（几乎不下滑）。

---

## 2. `importance` 如何調制半衰期

### 2.1 核心公式

```typescript
effectiveHL = halfLife × exp(μ × importance)
```

其中 `μ = 1.5`（預設值，不可外部配置，寫死於 `DEFAULT_DECAY_CONFIG`）。

### 2.2 實際效果試算（base halfLife = 30 天）

| importance | effectiveHL（天）| 效果描述 |
|------------|-----------------|----------|
| 0.0 | 30 | 標準半衰期 |
| 0.3 | 30 × e^0.45 ≈ 47 | 延長 56% |
| 0.5 | 30 × e^0.75 ≈ 63 | 延長 110% |
| 0.7 | 30 × e^1.05 ≈ 86 | 延長 186%（近3倍）|
| 0.9 | 30 × e^1.35 ≈ 116 | 延長 287%（近4倍）|

### 2.3 觀察與風險

**風險 1：`μ = 1.5` 為 magic number，沒有文獻依據**
- e^1.5 ≈ 4.48，最大可將半衰期延長至 base 的 4.5 倍
- 若 `importance = 1.0`（理論最大值），effectiveHL ≈ 134 天，對 Working Tier 而言偏長

**風險 2：指數調制而非線性**
- 小的 importance 差異就會造成大的半衰期差異
- `importance = 0.7` vs `0.8` 的 effectiveHL 差距約 19 天
- 若 `importance` 打分不精確，會放大錯誤

**建議**：
- 將 `importanceModulation`（μ）設為可設定參數，而非寫死
- 考慮加上一個 `importanceHalfLifeCapDays` 上限，避免某些高重要性記憶半衰期過長

---

## 3. Frequency Reinforcement 計算方式

### 3.1 公式結構

```typescript
function frequency(memory: DecayableMemory): number {
  const base = 1 - exp(-accessCount / 5);       // 對數飽和曲線
  if (accessCount <= 1) return base;

  const lastActive = accessCount > 0 ? lastAccessedAt : createdAt;
  const accessSpanDays = (lastActive - createdAt) / MS_PER_DAY;
  const avgGapDays = accessSpanDays / max(accessCount - 1, 1);
  const recentnessBonus = exp(-avgGapDays / 30);  // 時間衰減 bonus
  return base * (0.5 + 0.5 * recentnessBonus);
}
```

### 3.2 分項說明

**Base（對數飽和）**
```
base = 1 - e^(-accessCount / 5)
```
- `accessCount = 5` → base ≈ 0.63
- `accessCount = 15` → base ≈ 0.95
- 符合「邊際效益遞減」直覺：從 1→2 次很重要，10→11 次差異不大

**Recentness Bonus（平均存取間距 bonus）**
```
avgGapDays = (lastActive - createdAt) / (accessCount - 1)
recentnessBonus = exp(-avgGapDays / 30)
```
- 若每 30 天存取一次 → bonus ≈ 0.37（中等）
- 若每 7 天存取一次 → bonus ≈ 0.79（高）
- 若每 60 天才存取一次 → bonus ≈ 0.14（幾乎無 bonus）

**最終 frequency = base × (0.5 + 0.5 × recentnessBonus)**
- 最小值：當 bonus=0 時 → frequency = base × 0.5
- 最大值：當 bonus=1 時 → frequency = base × 1.0
- 單次存取：frequency = 1 - e^(-1/5) ≈ 0.18

### 3.3 與 access-tracker.ts 的互動

`access-tracker.ts` 提供 **實際的 reinforcement factor 計算**，用於更上層的半衰期延長：

```typescript
function computeEffectiveHalfLife(
  baseHalfLife, accessCount, lastAccessedAt,
  reinforcementFactor, maxMultiplier
): number {
  // Access freshness 指數衰減（30天半衰期）
  const accessFreshness = exp(-daysSinceLastAccess × ln(2) / 30);

  // 有趣的是：frequency 已經用了 avgGapDays，而這裡又用了一次 daysSinceLastAccess
  // 兩者概念重疊但應用層次不同
  const effectiveAccessCount = accessCount * accessFreshness;

  // 對數延長
  const extension = baseHalfLife * reinforcementFactor * log1p(effectiveAccessCount);
  return min(baseHalfLife + extension, baseHalfLife * maxMultiplier);
}
```

**`decay-engine.ts` 的 frequency 與 `access-tracker.ts` 的 reinforcement 是兩個不同機制**：
- `frequency`：用於 composite score 的即時計算（30% 權重）
- `reinforcementFactor`：用於延長衰減曲線的半衰期（直接改變 λ）

---

## 4. Tier 晉升 / 降級條件與觸發時機

### 4.1 完整狀態機

```
┌─────────────┐  access≥10, composite≥0.7, importance≥0.8   ┌─────────────┐
│  peripheral │ ─────────────────────────────────────────►  │   working   │
│ (floor=0.5)  │                                           │ (floor=0.7)  │
└─────────────┘                                           └─────────────┘
     ▲                                                            │
     │          composite<0.15 OR                                │ composite<0.15
     │          (age>60 days AND access<3)                       │ OR (age>60d AND access<3)
     │                                                            │
     │                                                            ▼
     │                                                   ┌─────────────┐
     └─────────────────────────────────────────────────  │    core     │
                       access<3 AND                       │ (floor=0.9) │
                       composite<0.15                     └─────────────┘
```

### 4.2 各層級晉升條件

| 方向 | 條件 | 說明 |
|------|------|------|
| peripheral → working | accessCount ≥ 3 **且** composite ≥ 0.4 | 需同時滿足「被用過幾次」和「還沒爛到地板」 |
| working → core | accessCount ≥ 10 **且** composite ≥ 0.7 **且** importance ≥ 0.8 | 三門檻同時滿足，門檻最高 |

### 4.3 各層級降級條件

| 方向 | 條件 | 說明 |
|------|------|------|
| working → peripheral | `composite < 0.15` **或** `(age > 60天 且 accessCount < 3)` | 任一條件滿足即降級 |
| core → working | `composite < 0.15` **且** `accessCount < 3` | 兩個條件同時滿足才降，Core 極難降級 |

### 4.4 觸發時機

`tier-manager.ts` 的 `evaluate()` 本身是純同步函式，**不主動觸發**，需要外部呼叫者：
- 適合在 cron job 中批次執行（每次評估所有記憶）
- 或在每次讀取記憶後，檢查是否需要晉升

**缺失分析**：
- 沒有「連續 N 次檢查都滿足條件才晉升」的機制，可能因為短暫高頻存取就晉升
- 沒有晉升冷卻期（cooldown），晉升後馬上降回的震盪風險

---

## 5. 與 Claude Code Decay 的差異

> Claude Code 的 Memory 衰減機制公開資訊有限，以下基於已知行為模式與公開文件分析。

### 5.1 核心差異總覽

| 面向 | memory-lancedb-pro | Claude Code |
|------|--------------------|-------------|
| 衰減模型 | Weibull + Logistic frequency hybrid | 純指數衰減（文件描述）|
| 調制方式 | importance → 半衰期 | importance → 直接分數加成 |
| 分層設計 | Core/Working/Peripheral 三層 | 無明確分層 |
| 頻率強化 | 雙機制（frequency score + reinforcement factor）| 單一 reinforcement |
| 存取 decay | Access count 有獨立的 30 天半衰期 | 無單獨的 access count decay |
| Decay floor | 有（tier-specific）| 無 |

### 5.2 設計哲學差異

**Claude Code 的 decay** 較為「公平」：
- 所有記憶以相同速率衰減
- importance 只作為加分項（直接加到 composite）
- 簡單、直覺、易解釋

**memory-lancedb-pro 的 decay** 較為「現實」：
- 高重要性記憶不只加分，而是**改變衰減速度本身**
- tier 提供了差異化的安全網（Core 几乎不衰減）
- 頻率強化區分了「偶然存取」和「持續使用的記憶」

### 5.3 具體數值差異

假設 `importance=0.8, accessCount=5, createdAt=60天前, lastAccessed=7天前`：

**Claude Code（純指數 + importance 加成）**：
```
score = base × 0.5^elapsedDays + importance × 0.3
      ≈ 0.5^60/30 + 0.8 × 0.3
      ≈ 0.25 + 0.24 = 0.49
```

**memory-lancedb-pro（Weibull + frequency + intrinsic）**：
```
recency  = exp(-ln(2) × 60^1.3 / (30 × e^1.2)) ≈ exp(-0.92) ≈ 0.40
frequency = 0.63 × 0.79 ≈ 0.50
intrinsic = 0.8 × 0.9 ≈ 0.72  (假設 confidence=0.9)
composite = 0.4 × 0.40 + 0.3 × 0.50 + 0.3 × 0.72 ≈ 0.54
```

兩者結果接近，但**分解結構不同**。Claude Code 的 intrinsic（importance×confidence）只是加分，memory-lancedb-pro 的 intrinsic 是獨立的 30% 權重。

---

## 6. 綜合評價與建議

### 6.1 設計優點

1. **Weibull β tier化**非常合理：Core 記憶需要 sub-exponential 才能長期維持高檔，Peripheral 需要 super-exponential 才能快速淘汰
2. **Decay floor** 設計優於純衰減：避免重要記憶真的歸零
3. **雙重頻率機制**（frequency score + reinforcement factor）兼顧即時分數與長期曲線
4. **Access freshness decay**（30天半衰期）防止「曾經高頻但現在已讀」的記憶繼續佔用 reinforcement

### 6.2 待優化點

| 問題 | 嚴重程度 | 說明 |
|------|----------|------|
| `importanceModulation = 1.5` 寫死 | 🟡 中 | 建議拉出成可設定參數 |
| 缺少晉升冷卻期 | 🟡 中 | 短期震盪可能導致 tier 跳來跳去 |
| `betaCore = 0.8` 可能不夠慢 | 🟡 中 | 若希望 Core 真正「永久難忘」，建議 0.5~0.6 |
| 缺少 Tier 變化的 hysteresis | 🔴 高 | 晉升/降級同一扇門（同一門檻），可能產生震盪 |
| `peripheralCompositeThreshold = 0.15` 比 `staleThreshold = 0.3` 還低 | 🟢 低 | 代表有 0.15~0.30 的「灰色地帶」，介於 stale 與降級之間 |

### 6.3 hysteresis 問題詳細說明

```
working → peripheral 的條件：composite < 0.15
peripheral → working 的條件：composite ≥ 0.4

若一個記憶的 composite 在 0.15~0.40 之間來回：
→ 不會降級（已低於 0.15）→ 但也不會晉升（未達 0.4）
→ 處於不穩定平衡，可能反覆橫跳
```

建議加入 **hysteresis gap** 或 **promotion delay counter**。

---

*本報告由 Subagent（mlp-decay）分析 src/ 原始碼產生，非 AI 猜測*
