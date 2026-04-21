/**
 * Auto-Recall Timing Test Script
 * 
 * 測試目標：驗證 auto-recall 各階段的耗時，找出瓶頸
 * 
 * 使用方式: node test_auto_recall_timing.js
 */

import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "os";
import { MemoryStore } from "./src/store.js";
import { JinaEmbedder } from "./src/embedder.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const pluginSdkStubPath = path.resolve(testDir, "test", "helpers", "openclaw-plugin-sdk-stub.mjs");

// 動態載入 with jiti alias
const jitiFactory = (await import("jiti")).default;
const jiti = jitiFactory(import.meta.url, {
  interopDefault: true,
  alias: { "openclaw/plugin-sdk": pluginSdkStubPath },
});

const { MemoryStore: StoreClass } = jiti("./src/store.ts");
const { JinaEmbedder: EmbedderClass } = jiti("./src/embedder.ts");

const VECTOR_DIM = 1024; // Jina v5
const TEST_WORK_DIR = mkdtempSync(path.join(tmpdir(), "auto-recall-timing-test-"));

// 測試配置
const CONFIG = {
  autoRecallTimeoutMs: 60000,
  autoRecallMaxChars: 1200,
  autoRecallPerItemMaxChars: 350,
  autoRecallMaxItems: 10,
  maxRecallPerTurn: 10,
  autoRecallMinRepeated: 2,
};

// 創建測試 store 和 embedder
async function createTestFixtures() {
  const store = new StoreClass({
    dbPath: path.join(TEST_WORK_DIR, "db"),
    vectorDim: VECTOR_DIM,
  });

  const embedder = new EmbedderClass({
    model: "jina/jina-embeddings-v5",
    apiKey: process.env.JINA_API_KEY || "test-key",
  });

  return { store, embedder };
}

// 生成測試記憶
function makeTestVector(dim = VECTOR_DIM, seed = 0) {
  const vec = new Array(dim);
  for (let i = 0; i < dim; i++) {
    vec[i] = (seed * 9301 + 49297) % 233280 / 233280; // 簡單偽隨機
  }
  return vec;
}

async function storeTestMemories(store, count = 20) {
  const memories = [];
  for (let i = 0; i < count; i++) {
    const text = `Test memory ${i}: ${"x".repeat(50 + (i % 10) * 20)}`;
    const vector = makeTestVector(VECTOR_DIM, i);
    const entry = await store.store({
      text,
      vector,
      category: i % 2 === 0 ? "fact" : "preference",
      scope: "global",
      importance: 0.5 + (i % 5) * 0.1,
    });
    memories.push(entry);
  }
  return memories;
}

// 測試1：單次 auto-recall 各階段耗時
async function testSingleRecallPhases(store, embedder) {
  console.log("\n=== 測試1: 單次 auto-recall 各階段耗時 ===");
  
  const phases = {
    embedQuery: 0,
    retrieve: 0,
    governance: 0,
    budget: 0,
    patchMetadata: 0,
    total: 0,
  };

  const query = "test query for memory recall";
  
  const startTotal = Date.now();
  
  // Phase 1: embedQuery
  let start = Date.now();
  try {
    await embedder.embedQuery(query);
  } catch (e) {
    console.log("  (embedder API call failed, skipping timing)");
  }
  phases.embedQuery = Date.now() - start;
  
  // Phase 2: retrieve
  start = Date.now();
  const results = await store.retrieve({ query, limit: 10, scopeFilter: ["global"] });
  phases.retrieve = Date.now() - start;
  
  // Phase 3: governance filtering
  start = Date.now();
  const filtered = results.filter(r => {
    const meta = JSON.parse(r.entry.metadata || "{}");
    return meta.state === "confirmed";
  });
  phases.governance = Date.now() - start;
  
  // Phase 4: budget selection
  start = Date.now();
  const selected = [];
  let usedChars = 0;
  for (const r of filtered) {
    if (selected.length >= CONFIG.autoRecallMaxItems) break;
    const meta = JSON.parse(r.entry.metadata || "{}");
    const text = meta.l0_abstract || r.entry.text;
    const chars = text.length;
    if (usedChars + chars <= CONFIG.autoRecallMaxChars) {
      selected.push({ ...r, chars });
      usedChars += chars;
    }
  }
  phases.budget = Date.now() - start;
  
  // Phase 5: patchMetadata (每個 selected item)
  start = Date.now();
  await Promise.allSettled(selected.slice(0, 3).map(async (r) => {
    await store.patchMetadata(r.entry.id, { injected_count: 1 });
  }));
  phases.patchMetadata = Date.now() - start;
  
  phases.total = Date.now() - startTotal;
  
  console.log("  各階段耗時:");
  console.log(`    embedQuery:      ${phases.embedQuery}ms`);
  console.log(`    retrieve:        ${phases.retrieve}ms`);
  console.log(`    governance:      ${phases.governance}ms`);
  console.log(`    budget:          ${phases.budget}ms`);
  console.log(`    patchMetadata:   ${phases.patchMetadata}ms`);
  console.log(`    ─────────────────────────`);
  console.log(`    TOTAL:           ${phases.total}ms`);
  
  return phases;
}

// 測試2：並發 auto-recall (模擬多批次)
async function testConcurrentRecall(store, embedder, concurrency = 5) {
  console.log(`\n=== 測試2: 並發 ${concurrency} 個 auto-recall 請求 ===`);
  
  const promises = Array.from({ length: concurrency }, async (_, i) => {
    const start = Date.now();
    try {
      const query = `concurrent query ${i}`;
      await embedder.embedQuery(query);
      const results = await store.retrieve({ query, limit: 5 });
      await Promise.allSettled(results.slice(0, 2).map(async (r) => {
        await store.patchMetadata(r.entry.id, { injected_count: 1 });
      }));
      return { id: i, success: true, duration: Date.now() - start };
    } catch (e) {
      return { id: i, success: false, duration: Date.now() - start, error: String(e) };
    }
  });
  
  const results = await Promise.all(promises);
  
  console.log("  結果:");
  for (const r of results) {
    const status = r.success ? "✅" : "❌";
    console.log(`    ${status} Request ${r.id}: ${r.duration}ms${r.error ? ` - ${r.error.slice(0, 50)}` : ""}`);
  }
  
  const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
  const maxDuration = Math.max(...results.map(r => r.duration));
  console.log(`  平均耗時: ${avgDuration.toFixed(0)}ms`);
  console.log(`  最大耗時: ${maxDuration}ms`);
  
  return results;
}

// 測試3：patchMetadata 鎖競爭
async function testMetadataPatchLockContention(store, itemCount = 10) {
  console.log(`\n=== 測試3: patchMetadata 鎖競爭 (${itemCount} 個更新) ===`);
  
  const memories = await storeTestMemories(store, itemCount);
  const ids = memories.map(m => m.id);
  
  const start = Date.now();
  await Promise.allSettled(ids.map(async (id) => {
    await store.patchMetadata(id, { injected_count: 1, last_injected_at: Date.now() });
  }));
  const duration = Date.now() - start;
  
  console.log(`  ${itemCount} 個 patchMetadata 耗時: ${duration}ms`);
  console.log(`  平均每個: ${(duration / itemCount).toFixed(0)}ms`);
  
  return duration;
}

// 主測試
async function main() {
  console.log("===========================================");
  console.log("Auto-Recall Timing Test");
  console.log("===========================================");
  console.log(`測試目錄: ${TEST_WORK_DIR}`);
  console.log(`Config:`, CONFIG);
  
  try {
    const { store, embedder } = await createTestFixtures();
    console.log("\n✅ Store 和 Embedder 初始化成功");
    
    // 存入測試記憶
    await storeTestMemories(store, 20);
    console.log("✅ 測試記憶存入成功 (20 筆)");
    
    // 執行測試
    await testSingleRecallPhases(store, embedder);
    await testConcurrentRecall(store, embedder, 5);
    await testMetadataPatchLockContention(store, 10);
    
    console.log("\n===========================================");
    console.log("測試完成");
    console.log("===========================================");
    
  } catch (error) {
    console.error("\n❌ 測試失敗:", error);
  } finally {
    // 清理
    try { rmSync(TEST_WORK_DIR, { recursive: true, force: true }); } catch {}
    console.log(`\n清理測試目錄: ${TEST_WORK_DIR}`);
  }
}

main();
