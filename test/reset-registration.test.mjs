/**
 * reset-registration.test.mjs
 *
 * 測試 resetRegistration() 的行為：
 * 1. 清除 WeakSet（替換為新實例）
 * 2. 清除 Map（clear()）
 * 3. 重置 singletonState
 * 4. 重置 hook event dedup set
 * 5. reset 後可正常重新 register
 */
import { describe, it } from 'node:test';
import assert from 'node:assert';

// ---------------------------------------------------------------------------
// Mock：完整的 dual-track 系統 + reset
// ---------------------------------------------------------------------------
function createDualTrackSystem() {
  // 使用 state 容器以便 reset 時可以替換 WeakSet（const 綁定到容器，容器屬性可變）
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
  };
}

// ---------------------------------------------------------------------------
// 測試
// ---------------------------------------------------------------------------
describe('resetRegistration()', () => {

  it('resetRegistration() clears Map (size becomes 0)', () => {
    const sys = createDualTrackSystem();
    sys.register({ id: 'api-1' });
    sys.register({ id: 'api-2' });
    assert.strictEqual(sys._registeredApisMap.size, 2);

    sys.resetRegistration();

    assert.strictEqual(sys._registeredApisMap.size, 0, 'Map should be empty');
  });

  it('resetRegistration() nullifies _singletonState', () => {
    const sys = createDualTrackSystem();
    sys.register({ id: 'api-1' });
    assert.notStrictEqual(sys._singletonState, null);

    sys.resetRegistration();

    assert.strictEqual(sys._singletonState, null, '_singletonState should be null');
  });

  it('resetRegistration() clears _hookEventDedup', () => {
    const sys = createDualTrackSystem();
    sys._hookEventDedup.add('bootstrap:agent:main:1:1000');
    sys._hookEventDedup.add('recall:agent:main:2:2000');
    assert.strictEqual(sys._hookEventDedup.size, 2);

    sys.resetRegistration();

    assert.strictEqual(sys._hookEventDedup.size, 0, 'hook dedup set should be empty');
  });

  it('resetRegistration() replaces WeakSet with fresh instance', () => {
    const sys = createDualTrackSystem();
    const api = { id: 'api-1' };
    sys.register(api);
    const oldWeakSet = sys._registeredApis;

    sys.resetRegistration();

    // Old WeakSet still has the api (GC can now collect it)
    assert.strictEqual(oldWeakSet.has(api), true, 'old WeakSet still has api');
    // New WeakSet (via getter) is the replacement — does not have api
    assert.strictEqual(sys._registeredApis.has(api), false, 'new WeakSet is fresh (does not have api)');
  });

  it('after reset, register() works normally (fresh start)', () => {
    const sys = createDualTrackSystem();

    // First session
    sys.register({ id: 'api-1' });
    assert.strictEqual(sys.initCallCount, 1);
    assert.strictEqual(sys._registeredApisMap.size, 1);

    sys.resetRegistration();
    assert.strictEqual(sys._registeredApisMap.size, 0);
    assert.strictEqual(sys._singletonState, null);

    // Second session — should start fresh
    sys.register({ id: 'api-2' });
    assert.strictEqual(sys.initCallCount, 2, 'init should be called again after reset');
    assert.strictEqual(sys._registeredApisMap.size, 1, 'Map should have new api');
    assert.notStrictEqual(sys._singletonState, null, 'singleton should be recreated');
  });

  it('multiple resets: each produces a fresh state', () => {
    const sys = createDualTrackSystem();

    sys.register({ id: 'api-1' });
    sys.resetRegistration();
    assert.strictEqual(sys._registeredApisMap.size, 0);

    sys.register({ id: 'api-2' });
    sys.resetRegistration();
    assert.strictEqual(sys._registeredApisMap.size, 0);

    sys.register({ id: 'api-3' });
    assert.strictEqual(sys._registeredApisMap.size, 1);
    assert.notStrictEqual(sys._singletonState, null);
  });

  it('reset while no registration: no-op, no errors', () => {
    const sys = createDualTrackSystem();

    assert.doesNotThrow(
      () => sys.resetRegistration(),
      'reset should be safe with no prior registration'
    );
    assert.strictEqual(sys._registeredApisMap.size, 0);
    assert.strictEqual(sys._singletonState, null);
  });

  it('_getRegisteredApisForTest() reflects reset immediately', () => {
    const sys = createDualTrackSystem();
    sys.register({ id: 'api-1' });
    assert.strictEqual(sys._getRegisteredApisForTest().size, 1);

    sys.resetRegistration();

    assert.strictEqual(sys._getRegisteredApisForTest().size, 0, 'exported Map should be empty after reset');
  });

  it('reset then register: WeakSet and Map stay in sync after reset cycle', () => {
    const sys = createDualTrackSystem();

    sys.register({ id: 'api-1' });
    sys.resetRegistration();

    const api2 = { id: 'api-2' };
    sys.register(api2);

    assert.strictEqual(sys._registeredApis.has(api2), true, 'WeakSet has api2');
    assert.strictEqual(sys._registeredApisMap.has(api2), true, 'Map has api2');
    assert.strictEqual(sys._getRegisteredApisForTest().get(api2), true);
  });
});
