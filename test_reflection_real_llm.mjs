/**
 * test_reflection_real_llm.mjs
 * =================================
 * 測試 reflection 生成的真實 LLM 耗時
 * 使用真實 MiniMax API key + MiniMax-M2.7 模型
 *
 * 使用方式：
 *   node --experimental-vm-modules test_reflection_real_llm.mjs
 */

import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = "C:\\Users\\admin\\.openclaw\\extensions\\memory-lancedb-pro";
const pluginSdkStubPath = path.join(repoRoot, "test", "helpers", "openclaw-plugin-sdk-stub.mjs");

// MiniMax API Key（從 openclaw.json env.vars.MINIMAX_API_KEY）
const MINIMAX_API_KEY = "sk-cp-q79Qyh-aAJ6TW9UYlsrPVacDxIXVL0y1V3ikDCTFg5_pph_uVHcur-KcQnKCJxIWtU_exr_FIzi6nRV-Njb-35exahgbc-XrWdWVadSB13qHriCEK6YewIU";
const MINIMAX_BASE_URL = "https://api.minimax.io/v1";
const MODEL = "MiniMax-M2.7";

const jitiFactory = (await import("jiti")).default;
const jiti = jitiFactory(import.meta.url, {
  interopDefault: true,
  alias: {
    "openclaw/plugin-sdk": pluginSdkStubPath,
  },
});

// ---------------------------------------------------------------------------
// 1. Swap embedder factory
// ---------------------------------------------------------------------------
const embedderModule = jiti("../src/embedder.ts");
function createRealOllamaEmbedder(config) {
  const apiKey = config.apiKey ?? "ollama";
  const baseURL = (config.baseURL ?? "http://localhost:11434/v1").replace(/\/$/, "");
  return {
    _config: config,
    async embedQuery(text, signal) {
      const t0 = Date.now();
      const resp = await fetch(`${baseURL}/api/embeddings`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
        body: JSON.stringify({ model: config.model ?? "jina-v5-retrieval-test", prompt: text }),
        signal,
      });
      if (!resp.ok) throw new Error(`embed failed: ${resp.status}`);
      const json = await resp.json();
      console.log(`    [embedQuery] ${Date.now() - t0}ms | ${text.length} chars | dims=${json.embedding?.length ?? 0}`);
      return json.embedding;
    },
    async embedPassage(text, signal) { return this.embedQuery(text, signal); },
    async embedBatchPassage(texts, signal) {
      const t0 = Date.now();
      // Ollama batch 不支援，改用單筆
      const results = [];
      for (const t of texts) {
        results.push(await this.embedQuery(t, signal));
      }
      console.log(`    [embedBatch] ${Date.now() - t0}ms | ${texts.length} texts`);
      return results;
    },
    async test() { return { success: true, dimensions: config.dimensions ?? 1024 }; },
  };
}
embedderModule.createEmbedder = createRealOllamaEmbedder;

// ---------------------------------------------------------------------------
// 2. Load plugin
// ---------------------------------------------------------------------------
const pluginModule = jiti("../index.ts");
const plugin = (pluginModule.default || pluginModule);

function createPluginApiHarness(pluginConfig, resolveRoot) {
  const eventHandlers = new Map();
  const timingLogs = [];
  const api = {
    pluginConfig,
    resolvePath(target) {
      if (typeof target !== "string") return target;
      return path.isAbsolute(target) ? target : path.join(resolveRoot, target);
    },
    logger: {
      info(...args)  { timingLogs.push({ level: "info", ts: Date.now(), msg: args.join(" ") }); console.log(`  [INFO] ${args.join(" ")}`); },
      warn(...args)  { timingLogs.push({ level: "warn", ts: Date.now(), msg: args.join(" ") }); console.log(`  [WARN] ${args.join(" ")}`); },
      debug(...args) { timingLogs.push({ level: "debug", ts: Date.now(), msg: args.join(" ") }); },
    },
    registerTool()   {},
    registerCli()    {},
    registerService() {},
    on(eventName, handler, meta) {
      const list = eventHandlers.get(eventName) || [];
      list.push({ handler, meta });
      eventHandlers.set(eventName, list);
    },
    registerHook(eventName, handler, opts) {
      const list = eventHandlers.get(eventName) || [];
      list.push({ handler, meta: opts });
      eventHandlers.set(eventName, list);
    },
  };
  return { api, eventHandlers, timingLogs };
}

const workDir = mkdtempSync(path.join(tmpdir(), "diag-reflection-real-llm-"));

// ---------------------------------------------------------------------------
// 3. 建立 session file（類比真實對話，16193 chars）
// ---------------------------------------------------------------------------
const SESSION_ID = "real-llm-test-session";
const SESSION_DIR = path.join(workDir, "sessions", SESSION_ID);
mkdirSync(SESSION_DIR, { recursive: true });
const SESSION_FILE = path.join(SESSION_DIR, "conversation.jsonl");

// 產生 16193 chars 的模擬對話
const longConversation = [];
let totalChars = 0;
let msgId = 0;

const sampleMessages = [
  { role: "user", content: "幫我分析這個錯誤" },
  { role: "assistant", content: "好的，這是常見的設定問題。讓我幫你檢查。" },
  { role: "user", content: "錯誤訊息是 Failed to generate embedding from Ollama" },
  { role: "assistant", content: "這是 Ollama embedding endpoint 的問題。/v1/embeddings 在 0.20.5 有 bug。" },
  { role: "user", content: "那要怎麼修復？" },
  { role: "assistant", content: "需要改用 /api/embeddings endpoint，並把 input 參數改成 prompt。" },
  { role: "user", content: "有測試過嗎？" },
  { role: "assistant", content: "測試過了，/api/embeddings + prompt 參數可以正常產出 1024 dims。" },
  { role: "user", content: "那 PR 什麼時候可以開？" },
  { role: "assistant", content: "我已經開了 Issue #620，現在等維護者確認方向。" },
];

while (totalChars < 16500) {
  for (const msg of sampleMessages) {
    const fullMsg = {
      type: "message",
      message: { role: msg.role, content: msg.content + ` (msg #${msgId})` }
    };
    longConversation.push(JSON.stringify(fullMsg));
    totalChars += msg.content.length + 20;
    msgId++;
    if (totalChars >= 16500) break;
  }
}

const CONVO_MESSAGES = longConversation.join("\n");
writeFileSync(SESSION_FILE, CONVO_MESSAGES, "utf-8");
console.log(`\n>>> Session file: ${SESSION_FILE}`);
console.log(`    Messages: ${msgId} | Chars: ${CONVO_MESSAGES.length}`);

// Self-improvement 目錄
mkdirSync(path.join(workDir, ".learnings", "error_signatures"), { recursive: true });

const DB_PATH = path.join(workDir, "db");

const PLUGIN_CONFIG = {
  autoCapture: false,
  autoRecall: false,
  autoRecallMaxQueryLength: 6000,
  autoRecallTimeoutMs: 60_000,
  dbPath: DB_PATH,
  embedding: {
    provider: "openai-compatible",
    apiKey: "ollama",
    baseURL: "http://localhost:11434/v1",
    dimensions: 1024,
    model: "jina-v5-retrieval-test",
    normalized: true,
  },
  enableManagementTools: false,
  sessionStrategy: "memoryReflection",
  scopes: { default: "global" },
  sessionMemory: { enabled: false },
  autoRecallMinRepeated: 2,
  mdMirror: { enabled: false },
  smartExtraction: false,
  selfImprovement: {
    enabled: false,
    beforeResetNote: false,
    ensureLearningFiles: false,
  },
  memoryReflection: {
    enabled: true,
    messageCount: 120,
    maxInputChars: 24000,
    timeoutMs: 120_000,
    thinkLevel: "none",
    excludeAgents: [],
  },
  // 使用真實 MiniMax API key + MiniMax-M2.7
  llm: {
    apiKey: MINIMAX_API_KEY,
    model: MODEL,
    baseURL: MINIMAX_BASE_URL,
  },
  retrieval: {
    mode: "hybrid",
  },
};

const { api, eventHandlers, timingLogs } = createPluginApiHarness(PLUGIN_CONFIG, repoRoot);

console.log("\n>>> Registering plugin ...");
plugin.register(api);

// ---------------------------------------------------------------------------
// 4. 找到 memory-reflection.command-reset hook
// ---------------------------------------------------------------------------
const commandResetHooks = eventHandlers.get("command:reset") || [];
const reflectionHook = commandResetHooks.find(h =>
  h.meta?.name === "memory-lancedb-pro.memory-reflection.command-reset"
);

if (!reflectionHook) {
  console.error("\nERROR: memory-reflection.command-reset hook not found!");
  process.exit(1);
}
console.log(`>>> Found: ${reflectionHook.meta?.name}`);
console.log(`>>> Model: ${MODEL}`);
console.log(`>>> MaxInputChars: 24000 | MessageCount: 120`);

// ---------------------------------------------------------------------------
// 5. 構造 /reset 事件
// ---------------------------------------------------------------------------
const RESET_SESSION_KEY = "agent:main:session:real-llm-test";

const resetEvent = {
  action: "reset",
  sessionKey: RESET_SESSION_KEY,
  timestamp: Date.now(),
  messages: ["你好，這是測試"],
  context: {
    commandSource: "user",
    sessionEntry: {
      sessionId: SESSION_ID,
      sessionFile: SESSION_FILE,
      provider: "discord",
      threadId: "12345",
    },
    previousSessionEntry: {
      sessionId: SESSION_ID,
      sessionFile: SESSION_FILE,
    },
    workspaceDir: workDir,
    cfg: PLUGIN_CONFIG,
  },
};

// ---------------------------------------------------------------------------
// 6. 執行
// ---------------------------------------------------------------------------
console.log("\n" + "=".repeat(60));
console.log("EXECUTING memory-reflection.command-reset WITH REAL MINIMAX");
console.log("=".repeat(60));

timingLogs.length = 0;
const t0 = Date.now();

try {
  await reflectionHook.handler(resetEvent, { cfg: PLUGIN_CONFIG });
  const totalMs = Date.now() - t0;
  console.log(`\n>>> Hook completed in ${totalMs} ms (${(totalMs/1000).toFixed(1)}s)`);
} catch (err) {
  const totalMs = Date.now() - t0;
  console.error(`\n>>> Hook ERROR after ${totalMs} ms: ${err.message}`);
  console.error(err.stack);
}

// ---------------------------------------------------------------------------
// 7. 顯示 timeline
// ---------------------------------------------------------------------------
if (timingLogs.length > 0) {
  console.log("\n" + "=".repeat(60));
  console.log("LOG TIMELINE");
  console.log("=".repeat(60));
  const tBase = timingLogs[0].ts;
  timingLogs.forEach(log => {
    const elapsed = (log.ts - tBase).toString().padStart(7);
    console.log(`[+${elapsed}ms] [${log.level}] ${log.msg}`);
  });
}

// ---------------------------------------------------------------------------
// 8. Cleanup
// ---------------------------------------------------------------------------
rmSync(workDir, { recursive: true, force: true });
console.log("\n>>> Cleanup done");
