import { mkdtempSync, rmSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import jitiFactory from "jiti";

const jiti = jitiFactory(import.meta.url, { interopDefault: true });
const { runCompaction } = jiti("../src/memory-compactor.ts");
const {
  DEFAULT_ERRORS_TEMPLATE,
  DEFAULT_LEARNINGS_TEMPLATE,
  ensureSelfImprovementLearningFiles,
} = jiti("../src/self-improvement-files.ts");

function deferred() {
  let resolve;
  const promise = new Promise((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

describe("async production paths", () => {
  let workDir;

  afterEach(() => {
    if (workDir) rmSync(workDir, { recursive: true, force: true });
    workDir = undefined;
  });

  function makeCompactionEntries(pairCount) {
    const entries = [];
    for (let pair = 0; pair < pairCount; pair++) {
      const angle = pair * 0.35;
      const vector = [Math.cos(angle), Math.sin(angle)];
      for (let member = 0; member < 2; member++) {
        entries.push({
          id: `memory-${pair}-${member}`,
          text: `memory ${pair} ${member}`,
          vector,
          category: "fact",
          scope: "global",
          importance: 0.9 - pair * 0.01,
          timestamp: Date.now() - 10_000,
          metadata: "{}",
        });
      }
    }
    return entries;
  }

  it("runs compaction plans with bounded parallelism", async () => {
    const entries = makeCompactionEntries(9);
    let activeStores = 0;
    let maxActiveStores = 0;
    const releaseStore = deferred();

    const store = {
      async fetchForCompaction() {
        return entries;
      },
      async store(entry) {
        activeStores += 1;
        maxActiveStores = Math.max(maxActiveStores, activeStores);
        await releaseStore.promise;
        activeStores -= 1;
        return { id: `merged-${entry.text}`, ...entry, timestamp: Date.now() };
      },
      async delete() {
        return true;
      },
    };

    const compaction = runCompaction(
      store,
      { async embedPassage() { return [1, 0]; } },
      {
        enabled: true,
        minAgeDays: 0,
        similarityThreshold: 0.999,
        minClusterSize: 2,
        maxMemoriesToScan: 100,
        dryRun: false,
        cooldownHours: 0,
      },
      undefined,
      { info() {}, warn() {} },
    );

    while (maxActiveStores < 4) {
      await new Promise((resolve) => setTimeout(resolve, 0));
    }
    assert.equal(maxActiveStores, 4);

    releaseStore.resolve();
    const result = await compaction;

    assert.equal(result.clustersFound, 9);
    assert.equal(result.memoriesCreated, 9);
    assert.equal(result.memoriesDeleted, 18);
    assert.equal(maxActiveStores, 4);
  });

  it("creates both self-improvement files through the production initializer", async () => {
    workDir = mkdtempSync(path.join(tmpdir(), "memory-lancedb-pro-async-files-"));

    await ensureSelfImprovementLearningFiles(workDir);

    const learnings = await readFile(path.join(workDir, ".learnings", "LEARNINGS.md"), "utf8");
    const errors = await readFile(path.join(workDir, ".learnings", "ERRORS.md"), "utf8");

    assert.equal(learnings, `${DEFAULT_LEARNINGS_TEMPLATE.trim()}\n`);
    assert.equal(errors, `${DEFAULT_ERRORS_TEMPLATE.trim()}\n`);
  });
});
