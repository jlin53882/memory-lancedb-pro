// isOwnedByAgent unit tests — Issue #448 fix verification
import { describe, it } from "node:test";
import assert from "node:assert";

// 從 reflection-store.ts 直接拷貝 isOwnedByAgent 函數（隔離測試）
function isOwnedByAgent(metadata, agentId) {
  const owner = typeof metadata.agentId === "string" ? metadata.agentId.trim() : "";

  const itemKind = metadata.itemKind;

  // derived：不做 main fallback，空白 owner → 完全不可見
  if (itemKind === "derived") {
    if (!owner) return false;
    return owner === agentId;
  }

  // invariant / legacy / mapped：維持原本的 main fallback
  if (!owner) return true;
  return owner === agentId || owner === "main";
}

describe("isOwnedByAgent — derived ownership fix (Issue #448)", () => {
  // === Must Fix 3: 缺少 derived 分支測試 ===
  describe("itemKind === 'derived'", () => {
    it("main's derived → main 可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "main" }, "main"), true);
    });
    it("main's derived → sub-agent 不可見（核心 bug fix）", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "main" }, "sub-agent-A"), false);
    });
    it("agent-x's derived → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x's derived → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "agent-x" }, "agent-y"), false);
    });
    it("derived + 空白 owner → 完全不可見（防呆）", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "" }, "main"), false);
      assert.strictEqual(isOwnedByAgent({ itemKind: "derived", agentId: "" }, "sub-agent"), false);
    });
  });

  describe("itemKind === 'invariant'（維持 fallback）", () => {
    it("main's invariant → sub-agent 可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "invariant", agentId: "main" }, "sub-agent-A"), true);
    });
    it("agent-x's invariant → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "invariant", agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x's invariant → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ itemKind: "invariant", agentId: "agent-x" }, "agent-y"), false);
    });
  });

  describe("legacy / mapped（無 itemKind，維持 fallback）", () => {
    it("main legacy → sub-agent 可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "main" }, "sub-agent-A"), true);
    });
    it("agent-x legacy → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x legacy → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "agent-x" }, "agent-y"), false);
    });
  });
});
