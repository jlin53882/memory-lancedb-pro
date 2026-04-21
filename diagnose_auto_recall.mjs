/**
 * Auto-Recall 瓶頸診斷腳本
 * 
 * 測試重點：
 * 1. embedQuery 耗時 (Jina API)
 * 2. retrieve 耗時 (LanceDB 檢索)
 * 3. patchMetadata 耗時 (檔案鎖競爭)
 * 
 * 使用方式: 
 *   1. 先設置 JINA_API_KEY 環境變量
 *   2. node diagnose_auto_recall.mjs
 */

import { fileURLToPath } from "node:url";
import path from "path";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "os";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN_PATH = "C:\\Users\\admin\\.openclaw\\extensions\\memory-lancedb-pro";
const TEST_DIR = mkdtempSync(path.join(tmpdir(), "auto-recall-diag-"));

// 使用 jiti 載入 TypeScript
function toFileUrl(winPath) {
  return 'file:///' + winPath.replace(/\\/g, '/').replace(/^([a-z]):/, (m) => m.slice(0,1).toLowerCase() + ':');
}
const jitiUrl = toFileUrl(path.join(PLUGIN_PATH, "node_modules", "jiti", "lib", "jiti.cjs"));
const jitiFactory = (await import(jitiUrl)).default;
const jiti = jitiFactory(import.meta.url, {
  interopDefault: true,
  alias: { "openclaw/plugin-sdk": toFileUrl(path.join(PLUGIN_PATH, "test", "helpers", "openclaw-plugin-sdk-stub.mjs")) },
});

// 載入必要模組
const { MemoryStore } = jiti(`${PLUGIN_PATH}/src/store.ts`);
const { createEmbedder } = jiti(`${PLUGIN_PATH}/src/embedder.ts`);

// 測試配置
const CONFIG = {
  dbPath: path.join(TEST_DIR, "db"),
  vectorDim: 1024, // Jina v5
  jinaApiKey: process.env.JINA_API_KEY || "",
};

// 診斷結果
const DIAG = {
  phases: {},
  errors: [],
};

async function init() {
  console.log("初始化 MemoryStore...");
  const store = new MemoryStore({
    dbPath: CONFIG.dbPath,
    vectorDim: CONFIG.vectorDim,
  });
  
  // 存入測試記憶
  console.log("存入測試記憶...");
  for (let i = 0; i < 20; i++) {
    const vector = new Array(CONFIG.vectorDim).fill(0).map(() => Math.random());
    await store.store({
      text: `測試記憶 ${i}: ${"x".repeat(100 + i * 10)}`,
      vector,
      category: "fact",
      scope: "global",
      importance: 0.7,
    });
  }
  console.log("測試記憶存入完成 (20 筆)");
  
  return store;
}

async function testEmbedQuery(store) {
  console.log("\n=== 測試1: embedQuery 耗時 ===");
  
  if (!CONFIG.jinaApiKey) {
    console.log("  ⚠️ JINA_API_KEY 未設置，跳過真實 API 測試");
    console.log("  建議：設置環境變量 JINA_API_KEY");
    return;
  }
  
  const embedder = createEmbedder({
    model: "jina/jina-embeddings-v5",
    apiKey: CONFIG.jinaApiKey,
  });
  
  const queries = [
    "測試查詢",
    "這是一個比較長的查詢內容用於測試",
    "多語言查詢 test 测试",
  ];
  
  for (const query of queries) {
    const start = Date.now();
    try {
      const vector = await embedder.embedQuery(query);
      console.log(`  ✅ embedQuery("${query.slice(0, 20)}..."): ${Date.now() - start}ms, vector[0]=${vector[0].toFixed(3)}`);
    } catch (err) {
      console.log(`  ❌ embedQuery FAILED: ${err.message.slice(0, 80)}`);
      DIAG.errors.push({ phase: "embedQuery", error: err.message });
    }
  }
}

async function testRetrieve(store) {
  console.log("\n=== 測試2: retrieve 耗時 ===");
  
  const queries = ["測試", "記憶", "x".repeat(200)];
  
  for (const query of queries) {
    const start = Date.now();
    try {
      const results = await store.retrieve({ query, limit: 10 });
      const duration = Date.now() - start;
      console.log(`  ✅ retrieve("${query.slice(0, 20)}..."): ${duration}ms, 找到 ${results.length} 筆`);
      DIAG.phases.retrieve = DIAG.phases.retrieve || [];
      DIAG.phases.retrieve.push(duration);
    } catch (err) {
      console.log(`  ❌ retrieve FAILED: ${err.message}`);
      DIAG.errors.push({ phase: "retrieve", error: err.message });
    }
  }
}

async function testPatchMetadata(store) {
  console.log("\n=== 測試3: patchMetadata 耗時 (單一請求) ===");
  
  // 先獲取一些記憶 ID
  const results = await store.retrieve({ query: "測試", limit: 5 });
  
  for (const r of results) {
    const start = Date.now();
    try {
      await store.patchMetadata(r.entry.id, {
        injected_count: 1,
        last_injected_at: Date.now(),
      });
      console.log(`  ✅ patchMetadata(${r.entry.id.slice(0, 8)}): ${Date.now() - start}ms`);
    } catch (err) {
      console.log(`  ❌ patchMetadata FAILED: ${err.message}`);
      DIAG.errors.push({ phase: "patchMetadata", error: err.message });
    }
  }
}

async function testConcurrentPatch(store) {
  console.log("\n=== 測試4: patchMetadata 並發耗時 (模擬多批次) ===");
  
  // 獲取所有記憶 ID
  const results = await store.retrieve({ query: "測試", limit: 20 });
  const ids = results.map(r => r.entry.id);
  
  console.log(`  並發更新 ${ids.length} 筆記憶...`);
  
  const start = Date.now();
  
  // 並發執行所有更新
  await Promise.allSettled(ids.map(async (id) => {
    const tStart = Date.now();
    await store.patchMetadata(id, {
      injected_count: Math.floor(Math.random() * 10),
      last_injected_at: Date.now(),
      bad_recall_count: Math.floor(Math.random() * 3),
    });
    return Date.now() - tStart;
  }));
  
  const totalDuration = Date.now() - start;
  console.log(`  ✅ 並發 patchMetadata 總耗時: ${totalDuration}ms`);
  console.log(`  平均每筆: ${(totalDuration / ids.length).toFixed(0)}ms`);
  
  DIAG.phases.concurrentPatch = totalDuration;
  
  // 測試更大並發
  console.log(`\n  測試更高並發 (50 個請求)...`);
  const manyIds = [...ids, ...ids, ...ids].slice(0, 50);
  
  const start2 = Date.now();
  await Promise.allSettled(manyIds.map(async (id) => {
    await store.patchMetadata(id, {
      injected_count: 1,
    });
  }));
  
  console.log(`  ✅ 高並發 patchMetadata (50) 總耗時: ${Date.now() - start2}ms`);
  DIAG.phases.highConcurrencyPatch = Date.now() - start2;
}

async function testSimulateRecallFlow(store, embedder) {
  console.log("\n=== 測試5: 模擬完整 auto-recall 流程 ===");
  
  if (!CONFIG.jinaApiKey || !embedder) {
    console.log("  ⚠️ 跳過 (需要 JINA_API_KEY)");
    return;
  }
  
  const phases = {
    embedQuery: 0,
    retrieve: 0,
    governance: 0,
    budget: 0,
    patchMetadata: 0,
    total: 0,
  };
  
  const query = "這是測試查詢";
  const autoRecallMaxChars = 1200;
  const autoRecallPerItemMaxChars = 350;
  const autoRecallMaxItems = 10;
  
  const startTotal = Date.now();
  
  // Phase 1: embedQuery
  const t1 = Date.now();
  const vector = await embedder.embedQuery(query);
  phases.embedQuery = Date.now() - t1;
  
  // Phase 2: retrieve
  const t2 = Date.now();
  const results = await store.retrieve({ query, limit: 20 });
  phases.retrieve = Date.now() - t2;
  
  // Phase 3: governance filtering
  const t3 = Date.now();
  const filtered = results.filter(r => {
    try {
      const meta = JSON.parse(r.entry.metadata || "{}");
      return meta.state === "confirmed" || !meta.state;
    } catch { return true; }
  });
  phases.governance = Date.now() - t3;
  
  // Phase 4: budget selection
  const t4 = Date.now();
  const selected = [];
  let usedChars = 0;
  for (const r of filtered) {
    if (selected.length >= autoRecallMaxItems) break;
    const meta = JSON.parse(r.entry.metadata || "{}");
    const text = meta.l0_abstract || r.entry.text;
    const chars = text.length;
    if (usedChars + chars <= autoRecallMaxChars) {
      selected.push({ ...r, chars });
      usedChars += chars;
    }
  }
  phases.budget = Date.now() - t4;
  
  // Phase 5: patchMetadata
  const t5 = Date.now();
  await Promise.allSettled(selected.slice(0, 3).map(async (r) => {
    await store.patchMetadata(r.entry.id, {
      injected_count: 1,
      last_injected_at: Date.now(),
    });
  }));
  phases.patchMetadata = Date.now() - t5;
  
  phases.total = Date.now() - startTotal;
  
  console.log("  各階段耗時:");
  console.log(`    embedQuery:      ${phases.embedQuery}ms`);
  console.log(`    retrieve:        ${phases.retrieve}ms`);
  console.log(`    governance:      ${phases.governance}ms`);
  console.log(`    budget:          ${phases.budget}ms`);
  console.log(`    patchMetadata:   ${phases.patchMetadata}ms`);
  console.log(`    ─────────────────────────`);
  console.log(`    TOTAL:           ${phases.total}ms`);
  
  DIAG.phases.fullFlow = phases;
  
  if (phases.total > 5000) {
    console.log(`\n  ⚠️ 警告: 總耗時 ${phases.total}ms 超過 5 秒！`);
    console.log(`    可能原因:`);
    if (phases.embedQuery > 1000) console.log(`    - embedQuery 過慢 (${phases.embedQuery}ms)`);
    if (phases.retrieve > 1000) console.log(`    - retrieve 過慢 (${phases.retrieve}ms)`);
    if (phases.patchMetadata > 1000) console.log(`    - patchMetadata 鎖競爭 (${phases.patchMetadata}ms)`);
  }
}

async function main() {
  console.log("===========================================");
  console.log("Auto-Recall 瓶頸診斷");
  console.log("===========================================");
  console.log(`測試目錄: ${TEST_DIR}`);
  console.log(`JINA_API_KEY: ${CONFIG.jinaApiKey ? "✅ 已設置" : "❌ 未設置"}`);
  
  let store;
  
  try {
    store = await init();
    
    await testEmbedQuery(store);
    await testRetrieve(store);
    await testPatchMetadata(store);
    await testConcurrentPatch(store);
    
    // 如果有 API key，測試完整流程
    if (CONFIG.jinaApiKey) {
      const embedder = createEmbedder({
        model: "jina/jina-embeddings-v5",
        apiKey: CONFIG.jinaApiKey,
      });
      await testSimulateRecallFlow(store, embedder);
    }
    
    // 總結
    console.log("\n===========================================");
    console.log("診斷總結");
    console.log("===========================================");
    
    if (DIAG.errors.length > 0) {
      console.log("\n錯誤:");
      DIAG.errors.forEach(e => console.log(`  - ${e.phase}: ${e.error.slice(0, 80)}`));
    }
    
    console.log("\n耗時分析:");
    if (DIAG.phases.retrieve) {
      const avg = (DIAG.phases.retrieve.reduce((a, b) => a + b, 0) / DIAG.phases.retrieve.length).toFixed(0);
      console.log(`  retrieve 平均: ${avg}ms`);
    }
    if (DIAG.phases.concurrentPatch) {
      console.log(`  並發 patchMetadata: ${DIAG.phases.concurrentPatch}ms`);
    }
    if (DIAG.phases.highConcurrencyPatch) {
      console.log(`  高並發 patchMetadata: ${DIAG.phases.highConcurrencyPatch}ms`);
    }
    if (DIAG.phases.fullFlow) {
      console.log(`  完整流程: ${DIAG.phases.fullFlow.total}ms`);
    }
    
    console.log("\n建議:");
    if (DIAG.phases.concurrentPatch > 5000) {
      console.log("  ⚠️ patchMetadata 耗時過長，可能是檔案鎖競爭");
      console.log("    建議: 減少並發請求或增加 autoRecallTimeoutMs");
    }
    
  } catch (error) {
    console.error("\n❌ 診斷失敗:", error);
  } finally {
    // 清理
    try { rmSync(TEST_DIR, { recursive: true, force: true }); } catch {}
    console.log(`\n清理測試目錄: ${TEST_DIR}`);
  }
}

main();
