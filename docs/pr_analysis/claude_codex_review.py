import subprocess, os

MINIMAX_API_KEY = "sk-cp-q79Qyh-aAJ6TW9UYlsrPVacDxIXVL0y1V3ikDCTFg5_pph_uVHcur-KcQnKCJxIWtU_exr_FIzi6nRV-Njb-35exahgbc-XrWdWVadSB13qHriCEK6YewIU"

PLAN = """你是記憶系統的專業架構師。請對以下 Proposal A 實作方案進行對抗性審查，用繁體中文回覆。

## 背景

這是 memory-lancedb-pro 的 feature PR 方案，需要提交進官方 CortexReach/memory-lancedb-pro master。

## 方案內容

### Stack Chain 架構
```
CortexReach/memory-lancedb-pro:master
  └── Phase 1 → PR against master
      └── Phase 3 → PR against Phase 1 branch
          └── Phase 4 → PR against Phase 3 branch
```

### Phase 1 實作
- agent_end hook (priority 20)：捕捉 agent 回應寫入 pendingRecall Map
- before_prompt_build hook (priority 5)：在下個 turn 評分 recall 使用情況
- session_end hook (priority 20)：清理 pendingRecall entries
- isRecallUsed() AND logic（ID + marker 都要存在才算確認使用）
- Per-recall scoring（每個 recallId 單獨計分，不互相污染）
- sessionKey:agentId composite key（防止跨 agent 干擾）
- bad_recall_count increment（在 error/miss path 中遞增）

### 已知的問題（提交 PR 前需要修復）
1. autoCapture block boundary：if (config.autoCapture !== false) 的 } 需要確認正確閉合
2. Phase 4 測試在測 mock 而非真實程式碼
3. Summary match 缺少 hasUsageMarker AND gate
4. 配置覆寫靜默失敗（confirmKeywords/errorKeywords 傳入 non-array 時 .some() 會失敗）

## 請對抗性審查以下問題

1. 設計漏洞：Phase 1 的 hooks 是否有 edge cases 未考慮？bad_recall_count increment 在 concurrent session 下是否有 race condition？

2. 實作風險：before_prompt_build 的 timing 是否正確？session_end 沒被觸發時 pendingRecall 會記憶體洩漏嗎？

3. 與官方程式碼整合：rebase 到最新 master 後最可能發生衝突的檔案是哪些？

4. 遺漏問題：這個方案有哪些我沒有注意到的问题？

5. 安全性：是否有安全疑慮（memory bloat、DoS）？

請用繁體中文輸出，每個問題都要有分析。P0 必須修復才能繼續的問題請標明。"""

print(f"Plan length: {len(PLAN)} chars")
print("Starting Claude Code adversarial review...")

env = os.environ.copy()
env['ANTHROPIC_BASE_URL'] = 'https://api.minimax.io/anthropic'
env['ANTHROPIC_AUTH_TOKEN'] = MINIMAX_API_KEY
env['ANTHROPIC_MODEL'] = 'minimax-portal/MiniMax-M2.7'

result = subprocess.run(
    ['claude', '--print', '--output-format', 'json', PLAN],
    capture_output=True, text=True, env=env, timeout=300
)

print(f"Exit code: {result.returncode}")
print(f"Stdout length: {len(result.stdout)}")
print(f"Stderr: {result.stderr[:500] if result.stderr else 'none'}")

if result.stdout:
    try:
        import json
        data = json.loads(result.stdout)
        content = data.get('content', [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    print("\n=== Claude Code Response ===")
                    print(block.get('text', '')[:5000])
        else:
            print(content[:5000])
    except Exception as e:
        print(f"Parse error: {e}")
        print(result.stdout[:2000])

with open("C:\\Users\\admin\\.openclaw\\workspace-dc-channel--1476866394556465252\\docs\\pr_analysis\\claude_review_result.txt", "w", encoding="utf-8") as f:
    if result.stdout:
        try:
            import json
            data = json.loads(result.stdout)
            content = data.get('content', [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        f.write(block.get('text', ''))
            else:
                f.write(str(content))
        except:
            f.write(result.stdout)
