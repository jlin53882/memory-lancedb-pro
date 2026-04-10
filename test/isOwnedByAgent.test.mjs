// isOwnedByAgent unit tests — Issue #448 fix verification
import { describe, it } from "node:test";
import assert from "node:assert";

// 從 reflection-store.ts 直接拷貝 isOwnedByAgent 函數（隔離測試）
function isOwnedByAgent(metadata, agentId) {
  const owner = typeof metadata.agentId === "string" ? metadata.agentId.trim() : "";
  const itemKind = metadata.itemKind;
  const type = metadata.type;
  if (type === "memory-reflection-item") {
    if (itemKind === "derived") {
      if (!owner) return false;
      return owner === agentId;
    }
    if (itemKind === "invariant") {
      if (!owner) return true;
      return owner === agentId || owner === "main";
    }
    return false; // 非法的 itemKind → fail-closed
  }
  if (!owner) return true;
  return owner === agentId || owner === "main";
}

describe("isOwnedByAgent — derived ownership fix (Issue #448)", () => {
  describe("itemKind === 'derived'", () => {
    it("main's derived → main 可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "main" }, "main"), true);
    });
    it("main's derived → sub-agent 不可見（核心 bug fix）", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "main" }, "sub-agent-A"), false);
    });
    it("agent-x's derived → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x's derived → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "agent-x" }, "agent-y"), false);
    });
    it("derived + 空白 owner → 完全不可見（防呆）", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "" }, "main"), false);
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "" }, "sub-agent"), false);
    });
  });

  describe("itemKind === 'invariant'（維持 fallback）", () => {
    it("main's invariant → sub-agent 可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "invariant", agentId: "main" }, "sub-agent-A"), true);
    });
    it("agent-x's invariant → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "invariant", agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x's invariant → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "invariant", agentId: "agent-x" }, "agent-y"), false);
    });
  });

  describe("Bug 3: malformed itemKind → fail-closed（PR #522 要求）", () => {
    it("itemKind='weird-kind' → sub-agent 不可見（fail-closed）", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "weird-kind", agentId: "main" }, "sub-agent"),
        false,
        "malformed itemKind should NOT fall back to owner==='main'"
      );
    });
    it("itemKind='' (空字串) → sub-agent 不可見（fail-closed）", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "", agentId: "main" }, "sub-agent"),
        false,
        "empty string itemKind should fail-closed"
      );
    });
    it("itemKind=123 (數字) → sub-agent 不可見（fail-closed）", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: 123, agentId: "main" }, "sub-agent"),
        false,
        "numeric itemKind should fail-closed"
      );
    });
    it("itemKind=null → sub-agent 不可見（fail-closed）", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: null, agentId: "main" }, "sub-agent"),
        false,
        "null itemKind should fail-closed"
      );
    });
    it("itemKind=undefined + type=memory-reflection-item → sub-agent 不可見（fail-closed）", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", agentId: "main" }, "sub-agent"),
        false,
        "undefined itemKind with type=memory-reflection-item should fail-closed"
      );
    });
    it("itemKind='legacy'（非法的 legacy 模擬）→ agent-x owner 也不可見", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "legacy", agentId: "agent-x" }, "agent-x"),
        false,
        "itemKind='legacy' should NOT be treated as legacy fallback — fail-closed"
      );
    });
    it("itemKind='mapped' → agent-x owner 也不可見", () => {
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "mapped", agentId: "agent-x" }, "agent-x"),
        false,
        "itemKind='mapped' should NOT be treated as mapped fallback — fail-closed"
      );
    });
  });

  describe("legacy / mapped（無 type=memory-reflection-item，維持 fallback）", () => {
    it("main legacy → sub-agent 可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "main" }, "sub-agent-A"), true);
    });
    it("agent-x legacy → agent-x 可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "agent-x" }, "agent-x"), true);
    });
    it("agent-x legacy → agent-y 不可見", () => {
      assert.strictEqual(isOwnedByAgent({ agentId: "agent-x" }, "agent-y"), false);
    });
    // legacy type（非 memory-reflection-item）
    it("type=memory-reflection（legacy）→ main 可被 sub-agent 見", () => {
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection", agentId: "main" }, "sub-agent"), true);
    });
  });
});
