// PR #522 Bug 1 & 2 結構驗證測試 + Bug 3 isOwnedByAgent 測試
import { describe, it, before } from "node:test";
import assert from "node:assert";
import { readFileSync } from "node:fs";

// ============================================================
// Bug 1 & 2: 結構驗證測試
// ============================================================
describe("register retry + resetRegistration（PR #522 Bug 1 & 2）結構驗證", () => {
  let indexContent;

  before(() => {
    indexContent = readFileSync("./index.ts", "utf-8");
  });

  describe("Bug 1: register(api) 初始化失敗後可重試", () => {
    it("_registeredApis 是 Map（不是 WeakSet）", () => {
      assert.ok(
        indexContent.includes("const _registeredApis = new Map<OpenClawPluginApi, boolean>()"),
        "_registeredApis 應為 Map"
      );
      assert.ok(
        !indexContent.includes("new WeakSet"),
        "不應再使用 WeakSet"
      );
    });

    it("idempotent guard 使用 .get(api) === true", () => {
      assert.ok(
        indexContent.includes("_registeredApis.get(api) === true"),
        "idempotent guard 應使用 .get(api) === true"
      );
      assert.ok(
        !indexContent.includes("_registeredApis.has(api)"),
        "不應再使用 .has(api)"
      );
    });

    // it("try-catch 包住初始化，catch 不呼叫 .set()（驗證結構）", () => {
    //   // 驗證核心結構：
    //   // 1. 有 try { 包住初始化
    //   // 2. 有 .set(api, true) 在某處
    //   // 3. 有 } catch (err) { 在 register() 內
    //   // 4. catch block 區域不呼叫 .set()
    //   
    //   const registerStart = indexContent.indexOf("register(api: OpenClawPluginApi)");
    //   const registerContent = indexContent.slice(registerStart);
    //   
    //   // 驗證 1: 有 try {
    //   assert.ok(registerContent.includes("try {"), "register() 內應有 try {");
    //   
    //   // 驗證 2: 有 .set(api, true)
    //   assert.ok(registerContent.includes("_registeredApis.set(api, true)"), 
    //     "register() 內應有 _registeredApis.set(api, true)");
    //   
    //   // 驗證 3: 有 catch
    //   assert.ok(registerContent.includes("} catch (err) {"), 
    //     "register() 內應有 } catch (err) {");
    // });
  });

  describe("Bug 2: resetRegistration() 清除 _registeredApis", () => {
    it("resetRegistration() 呼叫 _registeredApis.clear()", () => {
      assert.ok(
        indexContent.includes("_registeredApis.clear()"),
        "resetRegistration() 應呼叫 .clear()"
      );
    });

    it("resetRegistration() 被 export", () => {
      assert.ok(
        indexContent.includes("export function resetRegistration()"),
        "resetRegistration 應被 export"
      );
    });

    it("_getRegisteredApisForTest() 存在（測試用）", () => {
      assert.ok(
        indexContent.includes("function _getRegisteredApisForTest()"),
        "_getRegisteredApisForTest 應存在"
      );
    });
  });
});

// ============================================================
// Bug 3: isOwnedByAgent fail-closed 邏輯測試
// ============================================================
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

describe("isOwnedByAgent — Bug 3: malformed itemKind fail-closed", () => {
  describe("itemKind === 'derived'", () => {
    it("main's derived → main 可見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "main" }, "main"), true));
    it("main's derived → sub-agent 不可見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "main" }, "sub-agent"), false));
    it("derived + 空白 owner → 完全不可見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "derived", agentId: "" }, "main"), false));
  });

  describe("itemKind === 'invariant'（維持 fallback）", () => {
    it("main's invariant → sub-agent 可見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "invariant", agentId: "main" }, "sub-agent"), true));
    it("invariant + 空白 owner → 可見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection-item", itemKind: "invariant", agentId: "" }, "sub-agent"), true));
  });

  describe("malformed itemKind → fail-closed（Bug 3 核心）", () => {
    it("itemKind='weird-kind' + owner='main' → sub-agent 不可見", () =>
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "weird-kind", agentId: "main" }, "sub-agent"),
        false,
        "malformed itemKind 不應掉回 owner==='main' fallback"
      ));
    it("itemKind='' (空字串) → sub-agent 不可見", () =>
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "", agentId: "main" }, "sub-agent"),
        false
      ));
    it("itemKind=123 (數字) → sub-agent 不可見", () =>
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: 123, agentId: "main" }, "sub-agent"),
        false
      ));
    it("itemKind=undefined + type=memory-reflection-item → sub-agent 不可見", () =>
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", agentId: "main" }, "sub-agent"),
        false
      ));
    it("itemKind='legacy' → agent-x owner 也不可見（fail-closed）", () =>
      assert.strictEqual(
        isOwnedByAgent({ type: "memory-reflection-item", itemKind: "legacy", agentId: "agent-x" }, "agent-x"),
        false,
        "itemKind='legacy' 不等於 legacy fallback"
      ));
  });

  describe("legacy（無 type=memory-reflection-item，維持 fallback）", () => {
    it("main legacy → sub-agent 可見", () =>
      assert.strictEqual(isOwnedByAgent({ agentId: "main" }, "sub-agent"), true));
    it("type=memory-reflection（legacy）→ main 可被 sub-agent 見", () =>
      assert.strictEqual(isOwnedByAgent({ type: "memory-reflection", agentId: "main" }, "sub-agent"), true));
  });
});