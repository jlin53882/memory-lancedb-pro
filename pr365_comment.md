## PR Update

### PR #307 — autoRecallExcludeAgents has been ported to this PR

`autoRecallExcludeAgents` 功能（原本在 PR #307）已移植到本 PR，並配合新架構調整實作方式（`before_prompt_build` 而非已廢棄的 `before_agent_start`）。

新增變更：
- **`index.ts`**：`autoRecallExcludeAgents?: string[]` 介面 + `before_prompt_build` 等級的排除邏輯
- **`parsePluginConfig`**：解析並過濾空字串
- **`README.md`**：新增 Option C 說明文件

### Recommendation: close PR #307

`autoRecallExcludeAgents` 已在 #365 中完整實作，建議關閉 PR #307。

### Review Checklist
- [ ] `autoRecallExcludeAgents` 正確跳過指定 agent 的 injection
- [ ] `recallMode` 與 `autoRecallExcludeAgents` 共存無衝突
- [ ] `idempotent guard` + `governance logging` 完整保留
- [ ] `openclaw.plugin.json` schema 包含 `recallMode` 和 `autoRecallExcludeAgents`

@AliceLJY 麻煩檢查一下，確認沒問題後就可以 merge 了！
