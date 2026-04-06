import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

prompt = """請用繁體中文 review commit 484845d：
在 rerankApiKey/rerankEndpoint/rerankModel/rerankProvider 的 typeof string 檢查後加上 .includes("$EX") 防止空值解析失敗。
diff: if (typeof x === "string" && x.includes("$EX")) { x = resolveEnvVars(x); }
請確認：1)邏輯 2)副作用 3)風格"""

result = run_opencode_task(
    prompt=prompt,
    model="minimax/MiniMax-M2.7",
    reasoning="medium",
    auto_start=False,
)
print("OK:", result.ok)
print("TEXT:", result.text[:3000] if result.text else "(empty)")
if result.error:
    print("ERROR:", result.error)
