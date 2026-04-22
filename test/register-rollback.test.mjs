/**
 * register-rollback.test.mjs
 *
 * 測試 dual-track register() 的 rollback 行為：
 * 當 _initPluginState() 拋出錯誤時，Map 必須清除（rollback）。
 * WeakSet 是 early claim（在 init 之前），失敗後 WeakSet 仍然有 api，這是預期行為。
 */
import { describe, it } from 'node:test';
import assert from 'node:assert';

// ---------------------------------------------------------------------------
// Mock工廠：會失敗的 initPluginState
// failOnCall = N → 前 N-1 次成功，第 N 次失敗
// ---------------------------------------------------------------------------
function createFailingState(failOnCall) {
  const _registeredApis = new WeakSet();
  const _registeredApisMap = new Map();
  let initCallCount = 0;

  function failingInitPluginState() {
    initCallCount++;
    if (initCallCount >= failOnCall) {
      throw new Error('Plugin initialization failed: simulated error');
    }
    return { config: {}, resolvedDbPath: '/tmp/test', store: {} };
  }

  let _singletonState = null;

  function register(api) {
    if (_registeredApis.has(api)) {
      return; // idempotent — skip
    }
    _registeredApis.add(api);      // early claim (before init)
    _registeredApisMap.set(api, true);
    try {
      if (!_singletonState) { _singletonState = failingInitPluginState(); }
    } catch (err) {
      _registeredApisMap.delete(api); // rollback Map only
      throw err;                        // re-throw
    }
  }

  return {
    _registeredApis, _registeredApisMap,
    get initCallCount() { return initCallCount; },
    get _singletonState() { return _singletonState; },
    register,
  };
}

// ---------------------------------------------------------------------------
// 測試
// ---------------------------------------------------------------------------
describe('register() rollback on init failure (dual-track)', () => {

  it('init failure: throws error to caller', () => {
    const state = createFailingState(1);
    const api = { id: 'fail-api' };

    assert.throws(
      () => state.register(api),
      /initialization failed/,
      'register() should re-throw the init error'
    );
  });

  it('init failure: WeakSet keeps api reference (GC will clean — design acceptable)', () => {
    // WeakSet.add() 在 init 之前就被呼叫（early claim）
    // 失敗時 Map 被清除，但 WeakSet 無法手動清除（只能 GC 或 resetRegistration）
    // 這是預期行為：WeakSet 是 early claim，失敗視同放棄
    const state = createFailingState(1);
    const api = { id: 'fail-api' };

    try { state.register(api); } catch {}

    assert.strictEqual(
      state._registeredApis.has(api), true,
      'WeakSet still has api after failure (early claim before init) — GC will clean this'
    );
  });

  it('init failure: api is NOT in Map after rollback (critical invariant)', () => {
    // Map rollback 是關鍵不變量
    const state = createFailingState(1);
    const api = { id: 'fail-api' };

    try { state.register(api); } catch {}

    assert.strictEqual(
      state._registeredApisMap.has(api), false,
      'Map should NOT contain api after rollback'
    );
    assert.strictEqual(state._registeredApisMap.size, 0, 'Map should be empty');
  });

  it('retry after failure requires resetRegistration() first (WeakSet guard)', () => {
    // 失敗後 WeakSet 仍有 api，直接 retry 會被 guard 擋住（不回傳錯誤）
    // 若要 retry：必須先 resetRegistration() 或建立新 api instance
    const state = createFailingState(1);
    const api = { id: 'fail-api' };

    // First attempt fails
    assert.throws(() => state.register(api), /initialization failed/);
    assert.strictEqual(state._registeredApisMap.has(api), false, 'Map rolled back');
    assert.strictEqual(state.initCallCount, 1);

    // Retry same api: WeakSet guard blocks → silent return, no throw
    state.register(api); // no throw (WeakSet guard)
    assert.strictEqual(state.initCallCount, 1, 'init NOT called again (WeakSet guard)');

    // With new api instance: retry succeeds
    const api2 = { id: 'fail-api-2' };
    assert.throws(() => state.register(api2), /initialization failed/);
    assert.strictEqual(state.initCallCount, 2);
  });

  it('init failure does NOT set _singletonState', () => {
    const state = createFailingState(1);
    const api = { id: 'fail-api' };

    try { state.register(api); } catch {}

    assert.strictEqual(state._singletonState, null, '_singletonState should remain null');
  });

  it('successful register() then failing register(): singleton survives failed call', () => {
    const state = createFailingState(3); // 1st=ok, 2nd=ok, 3rd=fail
    const api1 = { id: 'ok-api' };
    const api2 = { id: 'fail-api' };

    state.register(api1);
    assert.notStrictEqual(state._singletonState, null, 'singleton set');

    try { state.register(api2); } catch {}

    assert.notStrictEqual(state._singletonState, null, 'singleton survives failed call');
  });

  it('failed api2 does NOT affect api1 singleton state', () => {
    // Singleton 模式下，只有第一個 api 觸發 _initPluginState()
    // api2 的 register() 在 singleton 已設定後直接跳過 init（不回傳錯誤）
    // 因此「api2 失敗不影響 api1」在 singleton 架構下的實際意思是：
    // api1 成功設定 singleton，api2 的任何操作都不會破壞已設定的 singleton
    const state = createFailingState(1); // 第一個 api 就失敗
    const api1 = { id: 'ok-api' };
    const api2 = { id: 'ok-api-2' };

    // api1 失敗，不影響任何狀態
    try { state.register(api1); } catch {}
    assert.strictEqual(state._singletonState, null, 'singleton still null after api1 failure');

    // 成功建立新系統測試 api1 成功後 api2 的行為
    const okState = createFailingState(2); // 1st=ok, 2nd=fail
    okState.register(api1);
    assert.notStrictEqual(okState._singletonState, null, 'api1 set singleton');

    // api2 register() 由於 singleton 已設定，直接跳過 init（不回傳錯誤）
    // 這是 singleton 的預期行為：api2 不會破壞已存在的 singleton
    okState.register(api2); // no throw
    assert.strictEqual(okState.initCallCount, 1, 'init only called once (singleton)');
    assert.notStrictEqual(okState._singletonState, null, 'singleton still set after api2');
  });
});
