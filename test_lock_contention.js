/**
 * Auto-Recall Lock Contention Test
 * 
 * 測試目標：驗證 store.patchMetadata 的檔案鎖競爭問題
 * 
 * 使用方式: node test_lock_contention.js
 */

import { existsSync, mkdirSync, rmSync, writeFileSync, unlinkSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

// 載入 lockfile 模組
import { default as lockfile } from "proper-lockfile";

const TEST_DIR = path.join(tmpdir(), `lock-test-${Date.now()}`);
mkdirSync(TEST_DIR, { recursive: true });

const LOCK_PATH = path.join(TEST_DIR, ".test.lock");

// 清理
function cleanup() {
  try { unlinkSync(LOCK_PATH); } catch {}
  try { rmSync(TEST_DIR, { recursive: true, force: true }); } catch {}
}

async function testLockRetries(concurrency = 10) {
  console.log(`\n=== 測試: ${concurrency} 個並發請求搶同一個鎖 ===`);
  
  // 確保 lock file 存在
  if (!existsSync(LOCK_PATH)) {
    writeFileSync(LOCK_PATH, "");
  }
  
  const tasks = Array.from({ length: concurrency }, async (_, i) => {
    const start = Date.now();
    let retries = 0;
    let success = false;
    
    try {
      const release = await lockfile.lock(LOCK_PATH, {
        retries: {
          retries: 10,
          factor: 2,
          minTimeout: 200,
          maxTimeout: 5000,
        },
        stale: 10000,
        onCompromised: (err) => {
          console.log(`  Request ${i}: lock compromised - ${err.message}`);
        },
      });
      
      retries = lockfile.check ? (await lockfile.check(LOCK_PATH) ? "locked" : "free") : "unknown";
      success = true;
      
      // 持有鎖一段時間
      await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
      
      await release();
    } catch (err) {
      console.log(`  ❌ Request ${i} FAILED after ${Date.now() - start}ms: ${err.message.slice(0, 60)}`);
      return { id: i, success: false, duration: Date.now() - start, error: err.message };
    }
    
    const duration = Date.now() - start;
    const status = success ? "✅" : "❌";
    console.log(`  ${status} Request ${i}: ${duration}ms (retries=${retries})`);
    
    return { id: i, success, duration };
  });
  
  const results = await Promise.all(tasks);
  
  const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
  const maxDuration = Math.max(...results.map(r => r.duration));
  const successCount = results.filter(r => r.success).length;
  
  console.log(`\n總結:`);
  console.log(`  成功率: ${successCount}/${concurrency}`);
  console.log(`  平均耗時: ${avgDuration.toFixed(0)}ms`);
  console.log(`  最大耗時: ${maxDuration}ms`);
  
  return results;
}

async function testStaleLock() {
  console.log(`\n=== 測試: 過期鎖清理 ===`);
  
  // 創建一個過期的鎖文件
  const staleLockPath = path.join(TEST_DIR, ".stale.lock");
  writeFileSync(staleLockPath, "stale-content");
  
  // 模擬過期（修改 mtime）
  const pastDate = new Date(Date.now() - 15 * 1000); // 15秒前
  const utimes = await import("node:fs/promises");
  try {
    await utimes.utimes(staleLockPath, pastDate, pastDate);
    console.log(`  創建過期鎖: ${staleLockPath}`);
    console.log(`  鎖年齡: 15秒 (> 10秒閾值)`);
    
    // 嘗試獲取過期鎖
    const release = await lockfile.lock(staleLockPath, {
      retries: { retries: 1 },
      stale: 10000, // 10秒
    });
    console.log(`  ✅ 成功獲取過期鎖 (自動清理)`);
    await release();
  } catch (err) {
    console.log(`  ❌ 獲取過期鎖失敗: ${err.message}`);
  }
}

async function main() {
  console.log("===========================================");
  console.log("Auto-Recall Lock Contention Test");
  console.log("===========================================");
  console.log(`測試目錄: ${TEST_DIR}`);
  console.log(`鎖路徑: ${LOCK_PATH}`);
  
  try {
    // 測試1: 基本並發鎖競爭
    await testLockRetries(10);
    
    // 測試2: 更高並發
    await testLockRetries(20);
    
    // 測試3: 過期鎖清理
    await testStaleLock();
    
    console.log("\n===========================================");
    console.log("測試完成");
    console.log("===========================================");
    
  } catch (error) {
    console.error("\n❌ 測試失敗:", error);
  } finally {
    cleanup();
  }
}

main();
