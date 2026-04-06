import sys, json
sys.path.insert(0, r"C:\Users\admin\.openclaw\workspace\skills\opencode-api\scripts")
from opencode_task import OpenCodeAPI

prompt = r"""請用繁體中文嚴格 review 以下 commit 的 3 個修復。**每個修復必須獨立判斷通過/需修改，並說明原因**。注意：請基於下面的 diff 來分析，不要猜測或假設任何程式碼內容。

=== COMMIT bd0c582 ===
fix(recall): AND logic in isRecallUsed + bad_recall_count increment fix

=== DIFF ===

--- a/src/reflection-slices.ts (isRecallUsed 函式) ---
舊邏輯：
  for (const marker of usageMarkers) {
    if (responseLower.includes(marker.toLowerCase())) {
      return true;  // OR logic：任一條件滿足就回傳
    }
  }
  for (const id of injectedIds) {
    if (id && responseLower.includes(id.toLowerCase())) {
      return true;
    }
  }

新邏輯：
  // Step 1: 先檢查 response 是否包含特定 ID
  const hasSpecificRecall = injectedIds.some(
    (id) => id && responseLower.includes(id.toLowerCase()),
  );
  // Step 2: 只有特定 ID 存在時，才檢查通用 usage phrase
  if (hasSpecificRecall) {
    const usageMarkers = [
      "remember",
      "之?\u3002",  // 原本的"記得"已被移除重複
    ];
    for (const marker of usageMarkers) {
      if (responseLower.includes(marker.toLowerCase())) {
        return true;
      }
    }
  }
  return false;

--- a/index.ts (bad_recall_count 修補) ---
舊邏輯（兩處）：
  await store.patchMetadata(recallId, { bad_recall_count: badCount }, undefined);
新邏輯（兩處）：
  await store.patchMetadata(recallId, { bad_recall_count: badCount + 1 }, undefined);

修復 1：isRecallUsed AND 邏輯重構
修復 2：bad_recall_count 遞增修補
修復 3：usageMarkers 去重（"記得"只留一個）

=== 請回答 ===

對每個修復：
1. 邏輯是否正確？
2. 是否有副作用或 regression？
3. 與原本 memory-lancedb-pro 的功能是否衝突？

最後結論：
- 修復 1：✅ 通過 / ❌ 需修改 + 原因
- 修復 2：✅ 通過 / ❌ 需修改 + 原因
- 修復 3：✅ 通過 / ❌ 需修改 + 原因

請嚴格把關。如果有任何問題，請明確說出來，不要只說「看起來 ok」。
"""

client = OpenCodeAPI(timeout=180)
sid = client.create_session(title="PR493-FixReview")
body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {
        "name": "MiniMax-M2.7",
        "providerID": "minimax",
        "modelID": "MiniMax-M2.7",
        "reasoningEffort": "high"
    }
}
r = client._req("POST", f"/session/{sid}/message", body)
text = client.extract_text(r)
print(text)
