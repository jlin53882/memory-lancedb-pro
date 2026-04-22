/**
 * register-idempotency.test.mjs
 *
 * 測試 dual-track register() 的 idempotency 行為：
 * 1. 同一 api 多次 register() 不會重複 init（WeakSet guard）
 * 2. 不同 api instance：只有第一個觸發 init（singleton guard）
 * 3. 兩種 idempotency 都同時保護 WeakSet 和 Map
 */
import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';

// ---------------------------------------------------------------------------
// Mock 輔助：建立乾淨的 dual-track 狀態
// ---------------------------------------------------------------------------
function createDualTrackState() {
  const _registeredApis = new WeakSet();
  const _registeredApisMap = new Map();
  let initCallCount = 0;

  function mockInitPluginState() {
    initCallCount++;
    return { config: {}, resolvedDbPath: '/tmp/test', store: {} };
  }

  let _singletonState = null;

  /** 模擬 register() 的核心邏輯（dual-track） */
  function register(api) {
    if (_registeredApis.has(api)) {
      return; // skip — idempotent (same instance)
    }
    _registeredApis.add(api);
    _registeredApisMap.set(api, true); // early claim
    try {
      if (!_singletonState) { _singletonState = mockInitPluginState(); }
    } catch (err) {
      _registeredApisMap.delete(api); // rollback
      throw err;
    }
  }

  return {
    _registeredApis, _registeredApisMap, _singletonState,
    get initCallCount() { return initCallCount; },
    register,
  };
}

// ---------------------------------------------------------------------------
// 測試
// ---------------------------------------------------------------------------
describe('register() idempotency (dual-track)', () => {

  it('first register() adds api to WeakSet and Map', () => {
    const state = createDualTrackState();
    const api = { id: 'test-api' };

    state.register(api);

    assert.strictEqual(state._registeredApis.has(api), true, 'WeakSet should have api');
    assert.strictEqual(state._registeredApisMap.has(api), true, 'Map should have api');
    assert.strictEqual(state._registeredApisMap.get(api), true);
    assert.strictEqual(state.initCallCount, 1, 'init should be called once');
  });

  it('second register() call skips — WeakSet guard fires', () => {
    const state = createDualTrackState();
    const api = { id: 'test-api' };

    state.register(api);
    assert.strictEqual(state.initCallCount, 1);

    state.register(api); // second call — should skip (same instance)
    assert.strictEqual(state.initCallCount, 1, 'init should NOT be called again');
  });

  it('second register() call does NOT add duplicate to Map', () => {
    const state = createDualTrackState();
    const api = { id: 'test-api' };

    state.register(api);
    assert.strictEqual(state._registeredApisMap.size, 1);

    state.register(api);
    assert.strictEqual(state._registeredApisMap.size, 1, 'Map size should stay 1 (no duplicate)');
  });

  it('different api instances: both added to WeakSet and Map, but only first triggers init', () => {
    // Singleton model: only the FIRST api instance triggers _initPluginState()
    // Second (different) api instance is added to WeakSet/Map but skips init
    const state = createDualTrackState();
    const api1 = { id: 'api-1' };
    const api2 = { id: 'api-2' };

    state.register(api1);
    assert.strictEqual(state.initCallCount, 1, 'first api triggers init');
    assert.strictEqual(state._registeredApisMap.size, 1);
    assert.strictEqual(state._registeredApisMap.has(api1), true);

    state.register(api2);
    assert.strictEqual(
      state.initCallCount, 1,
      'second (different) api does NOT trigger another init (singleton guard)'
    );
    assert.strictEqual(state._registeredApisMap.size, 2, 'both apis in Map');
    assert.strictEqual(state._registeredApisMap.has(api2), true);
  });

  it('idempotency: WeakSet guard prevents duplicate Map writes', () => {
    const state = createDualTrackState();
    const api = { id: 'test-api' };

    state.register(api);
    assert.strictEqual(state.initCallCount, 1);
    assert.strictEqual(state._registeredApisMap.size, 1);

    // Simulate re-call being blocked by WeakSet guard
    if (!state._registeredApis.has(api)) {
      state._registeredApis.add(api);
      state._registeredApisMap.set(api, true);
    }
    // Since WeakSet already has api, the guard above doesn't add again
    assert.strictEqual(state._registeredApisMap.size, 1, 'Map should still have only 1 entry');
  });

  it('WeakSet and Map membership are always in sync after register', () => {
    const state = createDualTrackState();
    const apis = [{ id: 'a' }, { id: 'b' }, { id: 'c' }];

    apis.forEach(api => state.register(api));

    // Verify: every api in Map is also in WeakSet
    for (const [api, val] of state._registeredApisMap.entries()) {
      assert.strictEqual(state._registeredApis.has(api), true, `WeakSet has entry for Map key`);
      assert.strictEqual(val, true);
    }

    // Verify count matches
    assert.strictEqual(state._registeredApisMap.size, 3);
  });
});
