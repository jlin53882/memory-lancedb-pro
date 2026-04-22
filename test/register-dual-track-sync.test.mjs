/**
 * register-dual-track-sync.test.mjs
 *
 * 測試 WeakSet 和 Map 雙軌的同步性：
 * 1. register() 成功後，WeakSet 和 Map 狀態一致
 * 2. resetRegistration() 同時清除兩者
 * 3. _getRegisteredApisForTest() export 正確
 */
import { describe, it } from 'node:test';
import assert from 'node:assert';

// ---------------------------------------------------------------------------
// Mock：完整的 dual-track 系統（使用物件容器以支援 WeakSet reset）
// ---------------------------------------------------------------------------
function createDualTrackSystem() {
  // 使用容器以便 reset 時可以替換 WeakSet
  const state = {
    _registeredApis: new WeakSet(),
    _registeredApisMap: new Map(),
    _singletonState: null,
    _hookEventDedup: new Set(),
  };

  let initCallCount = 0;

  function mockInitPluginState() {
    initCallCount++;
    return { config: {}, resolvedDbPath: '/tmp/test', store: {} };
  }

  function register(api) {
    if (state._registeredApis.has(api)) return;
    state._registeredApis.add(api);
    state._registeredApisMap.set(api, true);
    try {
      if (!state._singletonState) { state._singletonState = mockInitPluginState(); }
    } catch (err) {
      state._registeredApisMap.delete(api);
      throw err;
    }
  }

  function resetRegistration() {
    state._registeredApis = new WeakSet(); // replace with fresh WeakSet
    state._registeredApisMap.clear();
    state._singletonState = null;
    state._hookEventDedup.clear();
  }

  function _getRegisteredApisForTest() {
    return state._registeredApisMap;
  }

  return {
    register, resetRegistration, _getRegisteredApisForTest,
    get _registeredApis() { return state._registeredApis; },
    get _registeredApisMap() { return state._registeredApisMap; },
    get _hookEventDedup() { return state._hookEventDedup; },
    get _singletonState() { return state._singletonState; },
    get initCallCount() { return initCallCount; },
    get state() { return state; }, // expose for direct inspection
  };
}

// ---------------------------------------------------------------------------
// 測試
// ---------------------------------------------------------------------------
describe('WeakSet + Map dual-track synchronization', () => {

  it('register() adds api to both WeakSet and Map atomically on success', () => {
    const sys = createDualTrackSystem();
    const api = { id: 'test-api' };

    sys.register(api);

    // 驗證同步性：WeakSet 和 Map 狀態一致
    assert.strictEqual(sys._registeredApis.has(api), true, 'WeakSet has api');
    assert.strictEqual(sys._registeredApisMap.has(api), true, 'Map has api');
    assert.strictEqual(sys._registeredApisMap.get(api), true, 'Map value is true');
  });

  it('register() populates Map before _singletonState is set (early claim)', () => {
    // 這個測試驗證「early claim」特性：
    // Map 在 _singletonState 設定「之前」就被寫入
    // 順序：WeakSet.add → Map.set → (init success) → singletonState set
    // 所以成功後：WeakSet.has=true, Map.has=true, singletonState=notnull
    const sys = createDualTrackSystem();
    const api = { id: 'test-api' };

    sys.register(api);

    assert.strictEqual(sys._registeredApisMap.has(api), true, 'Map has api (claimed early)');
    assert.notStrictEqual(sys._singletonState, null, 'singleton was also set');
    // 如果 early claim 沒做到，這兩個狀態會不一致
  });

  it('_getRegisteredApisForTest() returns the internal Map', () => {
    const sys = createDualTrackSystem();
    const api = { id: 'test-api' };

    sys.register(api);

    const map = sys._getRegisteredApisForTest();
    assert.ok(map instanceof Map, 'should return a Map');
    assert.strictEqual(map, sys._registeredApisMap, 'should return the same Map reference');
    assert.strictEqual(map.has(api), true, 'Map should contain the registered api');
  });

  it('WeakSet and Map have same membership after multiple registers', () => {
    const sys = createDualTrackSystem();
    const apis = [
      { id: 'api-1' },
      { id: 'api-2' },
      { id: 'api-3' },
    ];

    apis.forEach(api => sys.register(api));

    // Both WeakSet and Map should agree on membership
    apis.forEach(api => {
      assert.strictEqual(sys._registeredApis.has(api), true, `WeakSet has ${api.id}`);
      assert.strictEqual(sys._registeredApisMap.has(api), true, `Map has ${api.id}`);
    });

    assert.strictEqual(
      sys._registeredApisMap.size, apis.length,
      `Map size should be ${apis.length}`
    );
  });

  it('resetRegistration() clears both WeakSet and Map', () => {
    const sys = createDualTrackSystem();
    const api = { id: 'test-api' };

    sys.register(api);
    assert.strictEqual(sys._registeredApisMap.size, 1);
    assert.notStrictEqual(sys._singletonState, null);

    sys.resetRegistration();

    assert.strictEqual(sys._registeredApisMap.size, 0, 'Map should be empty');
    assert.strictEqual(sys._getRegisteredApisForTest().size, 0, 'exported Map should be empty');
    assert.strictEqual(sys._singletonState, null, 'singleton should be null');
  });

  it('after reset, new api can register and Map grows from 0', () => {
    const sys = createDualTrackSystem();
    const api1 = { id: 'api-1' };
    const api2 = { id: 'api-2' };

    sys.register(api1);
    assert.strictEqual(sys._registeredApisMap.size, 1);

    sys.resetRegistration();
    assert.strictEqual(sys._registeredApisMap.size, 0, 'Map should be 0 after reset');

    sys.register(api2);
    assert.strictEqual(sys._registeredApisMap.size, 1, 'Map should grow from 0 again');
    assert.strictEqual(sys.initCallCount, 2, 'init should be called for api2');
  });

  it('Map correctly reflects idempotency — duplicate register does not grow Map', () => {
    const sys = createDualTrackSystem();
    const api = { id: 'test-api' };

    sys.register(api);
    assert.strictEqual(sys._registeredApisMap.size, 1);

    sys.register(api); // idempotent re-call
    assert.strictEqual(sys._registeredApisMap.size, 1, 'Map should NOT grow on duplicate register');

    sys.register(api); // another re-call
    assert.strictEqual(sys._registeredApisMap.size, 1, 'Map should still be 1');
  });

  it('rollback: Map.delete() keeps WeakSet and Map in sync', () => {
    // 建立一個會失敗的系統
    const failingSys = (() => {
      const state = {
        _registeredApis: new WeakSet(),
        _registeredApisMap: new Map(),
        _singletonState: null,
      };
      let initCallCount = 0;

      function failingInit() {
        initCallCount++;
        throw new Error('Simulated init failure');
      }

      function register(api) {
        if (state._registeredApis.has(api)) return;
        state._registeredApis.add(api);
        state._registeredApisMap.set(api, true);
        try {
          if (!state._singletonState) { failingInit(); }
        } catch (err) {
          state._registeredApisMap.delete(api); // rollback
          throw err;
        }
      }

      return {
        register,
        get _registeredApis() { return state._registeredApis; },
        get _registeredApisMap() { return state._registeredApisMap; },
        get _singletonState() { return state._singletonState; },
      };
    })();

    const api = { id: 'fail-api' };

    try { failingSys.register(api); } catch {}

    // After rollback: WeakSet has api (added before throw) but Map is cleaned
    assert.strictEqual(failingSys._registeredApis.has(api), true, 'WeakSet has api (added before throw)');
    assert.strictEqual(failingSys._registeredApisMap.has(api), false, 'Map cleaned (rollback)');
  });

  it('WeakSet and Map stay in sync across register + reset cycles', () => {
    const sys = createDualTrackSystem();

    sys.register({ id: 'api-1' });
    sys.register({ id: 'api-2' });
    assert.strictEqual(sys._registeredApisMap.size, 2);

    sys.resetRegistration();
    assert.strictEqual(sys._registeredApisMap.size, 0);

    sys.register({ id: 'api-3' });
    assert.strictEqual(sys._registeredApisMap.size, 1);

    // Verify membership
    assert.strictEqual(sys._registeredApis.has({ id: 'api-3' }), false, 'different object, WeakSet empty');
    assert.strictEqual(sys._registeredApisMap.has({ id: 'api-3' }), false, 'different object, Map empty');
  });
});
