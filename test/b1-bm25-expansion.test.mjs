import { describe, it } from "node:test";
import assert from "node:assert/strict";
import jitiFactory from "jiti";

const jiti = jitiFactory(import.meta.url, { interopDefault: true });
const { expandDerivedWithBm25 } = jiti("../src/bm25-expansion.ts");

function createMockStore(bm25Hits = []) {
  return {
    async bm25Search(query, limit, scopeFilter) {
      return bm25Hits.map((hit) => ({
        entry: hit.entry,
        score: 0.8,
      }));
    },
  };
}

function createMockApi() {
  return {
    logger: {
      debug: () => {},
      info: () => {},
      warn: () => {},
    },
  };
}

describe("expandDerivedWithBm25", () => {
  describe("D1: dedupe neighbors against derived (self-match guard)", () => {
    it("should exclude non-reflection neighbors that match original derived text", async () => {
      // A non-reflection memory entry whose text is identical to a derived line
      // should be excluded from neighbors — it is a reflection mirror/duplicate.
      const store = createMockStore([
        { entry: { id: "mirror1", text: "derived 1", category: "fact", scope: "global" } },
        { entry: { id: "mirror2", text: "derived 2", category: "note", scope: "global" } },
        { entry: { id: "genuine", text: "genuine neighbor fact", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = ["derived 1", "derived 2", "derived 3"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      // The two mirror entries must not appear — they match derived lines
      assert.ok(!result.includes("derived 1"), "Mirror of derived 1 must not appear");
      assert.ok(!result.includes("derived 2"), "Mirror of derived 2 must not appear");
      // Genuine neighbor should still be included
      assert.ok(result.includes("genuine neighbor fact"), "Genuine neighbor should appear");
    });

    it("should not deduplicate neighbors from different derived lines if text differs", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "neighbor A", category: "fact", scope: "global" } },
        { entry: { id: "2", text: "neighbor B", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1", "derived2"], ["global"], store, api);
      assert.ok(result.length >= 2, "Neighbors with different text should both appear");
    });
  });

  describe("D2: scopeFilter !== undefined guard", () => {
    it("should return derived unchanged when scopeFilter is undefined", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "neighbor", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = ["derived1", "derived2"];
      const result = await expandDerivedWithBm25(derived, undefined, store, api);
      assert.deepStrictEqual(result, derived);
    });

    it("should process normally when scopeFilter is provided", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "neighbor fact", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = ["derived1"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.ok(result.length >= 1);
    });
  });

  describe("D3: Cap at 16 total", () => {
    it("should cap total output at 16 items", async () => {
      const hits = Array.from({ length: 20 }, (_, i) => ({
        entry: { id: String(i), text: `neighbor ${i} some extra content here`, category: "fact", scope: "global" },
      }));
      const store = createMockStore(hits);
      const api = createMockApi();
      const derived = Array.from({ length: 10 }, (_, i) => `derived ${i}`);
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.ok(result.length <= 16, `Expected <= 16, got ${result.length}`);
    });
  });

  describe("D4: Truncate to first line, 120 chars", () => {
    it("should truncate neighbor text to first line and 120 chars", async () => {
      const longText = "first line\nsecond line that should be truncated " + "x".repeat(150);
      const store = createMockStore([
        { entry: { id: "1", text: longText, category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
      const neighbor = result[0];
      assert.ok(neighbor.length <= 120, `Expected <= 120, got ${neighbor.length}`);
      assert.ok(!neighbor.includes("\n"), "Should not contain newline");
    });
  });

  describe("D6: Merge (expand, not replace) — neighbors before base", () => {
    it("should place neighbors before derived base items", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "neighbor text", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = ["base derived 1", "base derived 2"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.ok(result.length >= 3, `Expected at least 3, got ${result.length}`);
      assert.strictEqual(result[0], "neighbor text");
      assert.strictEqual(result[1], "base derived 1");
      assert.strictEqual(result[2], "base derived 2");
    });

    it("should return neighbors first when prompt does .slice(0, 6)", async () => {
      const neighbors = [
        { entry: { id: "1", text: "neighbor 1", category: "fact", scope: "global" } },
        { entry: { id: "2", text: "neighbor 2", category: "fact", scope: "global" } },
        { entry: { id: "3", text: "neighbor 3", category: "fact", scope: "global" } },
      ];
      const store = createMockStore(neighbors);
      const api = createMockApi();
      const derived = ["base 1", "base 2", "base 3", "base 4", "base 5", "base 6"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      const firstSix = result.slice(0, 6);
      assert.ok(firstSix.some((t) => t.startsWith("neighbor")), "Neighbors should appear in first 6");
    });
  });

  describe("Issue 2: Filter out category: reflection (self-match)", () => {
    it("should exclude reflection category entries from neighbors", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "reflection entry", category: "reflection", scope: "global" } },
        { entry: { id: "2", text: "fact entry", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
      const reflectionEntries = result.filter((t) => t === "reflection entry");
      assert.strictEqual(reflectionEntries.length, 0, "Reflection entries should be excluded");
      assert.ok(result.some((t) => t === "fact entry"), "Fact entries should be included");
    });
  });

  describe("Fail-safe: bm25Search errors caught", () => {
    it("should not throw when bm25Search fails", async () => {
      const store = {
        async bm25Search() {
          throw new Error("BM25 search failed");
        },
      };
      const api = createMockApi();
      const derived = ["derived1", "derived2"];
      await assert.doesNotReject(() => expandDerivedWithBm25(derived, ["global"], store, api));
    });

    it("should return derived unchanged when bm25Search errors", async () => {
      const store = {
        async bm25Search() {
          throw new Error("BM25 search failed");
        },
      };
      const api = createMockApi();
      const derived = ["derived1", "derived2"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.deepStrictEqual(result, derived);
    });
  });

  describe("Bug fixes", () => {
    describe("Bug C: empty / whitespace-only neighbor text must be excluded", () => {
      it("should skip neighbor text that is empty string", async () => {
        const store = createMockStore([
          { entry: { id: "n1", text: "", category: "fact", scope: "global" } },
          { entry: { id: "n2", text: "valid text", category: "fact", scope: "global" } },
        ]);
        const api = createMockApi();
        const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
        assert.ok(!result.includes(""), "Empty string must not appear in neighbors");
        assert.ok(result.includes("valid text"), "Valid text should appear");
      });

      it("should skip neighbor text that is whitespace-only", async () => {
        const store = createMockStore([
          { entry: { id: "n1", text: "   \t\n  ", category: "fact", scope: "global" } },
          { entry: { id: "n2", text: "valid neighbor", category: "fact", scope: "global" } },
        ]);
        const api = createMockApi();
        const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
        assert.ok(!result.some((t) => t.trim() === ""), "Whitespace-only string must not appear in neighbors");
        assert.ok(result.includes("valid neighbor"), "Valid neighbor should appear");
      });

      it("should skip neighbor text that is only whitespace after first-line truncation", async () => {
        // entry.text is "\n   " — first line is empty after split
        const store = createMockStore([
          { entry: { id: "n1", text: "\n   second line", category: "fact", scope: "global" } },
        ]);
        const api = createMockApi();
        const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
        assert.ok(result.every((t) => t.trim() !== ""), "No empty/whitespace-only items should appear");
      });
    });

    describe("Bug D: non-reflection copy of derived text must be excluded (self-match dedup)", () => {
      it("should exclude non-reflection entry that exactly matches a derived line", async () => {
        const store = createMockStore([
          // This is a non-reflection memory that happens to contain the same text
          // as a derived line from a reflection entry. It should not appear as neighbor.
          { entry: { id: "mirror", text: "derived line content", category: "note", scope: "global" } },
          { entry: { id: "fact1", text: "some other fact", category: "fact", scope: "global" } },
        ]);
        const api = createMockApi();
        const derived = ["derived line content", "another derived line"];
        const result = await expandDerivedWithBm25(derived, ["global"], store, api);
        assert.ok(!result.includes("derived line content"), "Non-reflection mirror of derived must be excluded");
        assert.ok(result.includes("some other fact"), "Unrelated facts should appear");
      });

      it("should exclude non-reflection entry that matches derived after first-line truncation", async () => {
        // Long derived line truncated to 120 chars — a non-reflection entry
        // with the same 120-char prefix should still be excluded.
        const prefix = "x".repeat(120);
        const store = createMockStore([
          { entry: { id: "mirror", text: prefix + " extra detail not shown in first 120", category: "fact", scope: "global" } },
          { entry: { id: "unique", text: "unique neighbor fact", category: "fact", scope: "global" } },
        ]);
        const api = createMockApi();
        const derived = [prefix];
        const result = await expandDerivedWithBm25(derived, ["global"], store, api);
        assert.ok(!result.includes(prefix + " extra detail not shown in first 120"), "Mirror entry with same 120-char prefix must be excluded");
        assert.ok(result.includes("unique neighbor fact"), "Unrelated neighbor should appear");
      });
    });
  });

  describe("Edge cases", () => {
    it("should return empty array unchanged", async () => {
      const store = createMockStore([]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25([], ["global"], store, api);
      assert.deepStrictEqual(result, []);
    });

    it("should handle derived with more than 16 items by taking first 16", async () => {
      const store = createMockStore([
        { entry: { id: "1", text: "neighbor", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = Array.from({ length: 20 }, (_, i) => `derived ${i}`);
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.ok(result.length <= 16, `Expected <= 16, got ${result.length}`);
    });

    it("should skip expansion and return first 16 derived when derived.length === 16", async () => {
      let callCount = 0;
      const store = {
        async bm25Search() { callCount++; return []; },
      };
      const api = createMockApi();
      const derived = Array.from({ length: 16 }, (_, i) => `derived ${i}`);
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.equal(callCount, 0, "bm25Search should not be called when MAX_NEIGHBORS <= 0");
      assert.equal(result.length, 16);
    });

    it("should return derived unchanged when all bm25Search calls return empty", async () => {
      const store = {
        async bm25Search() { return []; },
      };
      const api = createMockApi();
      const derived = ["derived A", "derived B"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.deepStrictEqual(result, derived);
    });

    it("should handle bm25Search returning fewer than 2 hits per query", async () => {
      const store = {
        async bm25Search(query) {
          if (query === "derived1") {
            return [{ entry: { id: "n1", text: "neighbor one", category: "fact", scope: "global" } }];
          }
          return [];
        },
      };
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1", "derived2"], ["global"], store, api);
      assert.strictEqual(result[0], "neighbor one");
      assert.strictEqual(result[1], "derived1");
      assert.strictEqual(result[2], "derived2");
    });

    it("should handle neighbors + derived === 16 exactly (no truncation)", async () => {
      const store = createMockStore([
        { entry: { id: "n1", text: "neighbor one", category: "fact", scope: "global" } },
        { entry: { id: "n2", text: "neighbor two", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const derived = Array.from({ length: 14 }, (_, i) => `derived ${i}`);
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.equal(result.length, 16, `Expected exactly 16, got ${result.length}`);
      assert.strictEqual(result[0], "neighbor one");
      assert.strictEqual(result[1], "neighbor two");
      assert.strictEqual(result[2], "derived 0");
    });

    it("should stop after reaching MAX_NEIGHBORS even if more derived lines exist", async () => {
      let callCount = 0;
      const store = {
        async bm25Search() {
          callCount++;
          return [
            { entry: { id: `n${callCount}-a`, text: `neighbor ${callCount}a`, category: "fact", scope: "global" } },
            { entry: { id: `n${callCount}-b`, text: `neighbor ${callCount}b`, category: "fact", scope: "global" } },
          ];
        },
      };
      const api = createMockApi();
      // derived=6 → MAX_NEIGHBORS=10 → 5 iterations (each 2 hits) → outer breaks before 6th line
      const derived = ["d1", "d2", "d3", "d4", "d5", "d6"];
      const result = await expandDerivedWithBm25(derived, ["global"], store, api);
      assert.equal(callCount, 5, `Expected 5 bm25Search calls, got ${callCount}`);
      // 5 iterations × 2 hits = 10 neighbors + 6 derived = 16 (capped at 16)
      assert.equal(result.length, 16, `Expected 16 items, got ${result.length}`);
    });

    it("should handle null entry.text gracefully (OR '' guard before split)", async () => {
      const store = createMockStore([
        { entry: { id: "n1", text: null, category: "fact", scope: "global" } },
        { entry: { id: "n2", text: undefined, category: "fact", scope: "global" } },
        { entry: { id: "n3", text: "valid text", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
      // null → "" → (empty guard) excluded
      // undefined entry → hit.entry is undefined → reflection filter skips, empty guard skips
      // valid text → "valid text"
      const emptyCount = result.filter((t) => t === "").length;
      assert.equal(emptyCount, 0, `Expected 0 empty strings (null now filtered), got ${emptyCount}`);
      assert.ok(result.includes("valid text"), "valid text should be preserved");
      // n1 (null) and n2 (undefined→empty) are both excluded
      assert.equal(result.length, 1, `Expected 1 valid item, got ${result.length}`);
    });

    it("should dedupe by text snippet, not by entry.id", async () => {
      const samePrefix = "a".repeat(120);
      const store = createMockStore([
        { entry: { id: "id1", text: samePrefix + " — extra detail for id1", category: "fact", scope: "global" } },
        { entry: { id: "id2", text: samePrefix + " — extra detail for id2", category: "fact", scope: "global" } },
      ]);
      const api = createMockApi();
      const result = await expandDerivedWithBm25(["derived1"], ["global"], store, api);
      const firstResult = result[0];
      assert.ok(firstResult.startsWith(samePrefix));
      const count = result.filter((t) => t.startsWith(samePrefix)).length;
      assert.equal(count, 1, "Two entries with same 120-char prefix should be deduped to 1");
    });
  });
});
