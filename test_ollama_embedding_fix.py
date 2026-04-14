#!/usr/bin/env python3
"""
測試腳本：驗證 Ollama 0.20.5 embedding 修復方案

問題：Ollama 0.20.5 的 /v1/embeddings endpoint 有問題，所有參數都回傳空陣列
解決：改用 /api/embeddings endpoint + prompt 參數

這個腳本模擬 embedder.ts 修改後的行為，確認能正常產出 embedding。
"""

import requests
import time
import json

OLLAMA_BASE = "http://127.0.0.1:11434"
TEST_MODEL = "nomic-embed-text:latest"
TIMEOUT = 30

def test_legacy_api_with_prompt():
    """測試 Ollama legacy API (/api/embeddings) + prompt 參數"""
    print("\n=== 測試 1: Legacy API + prompt 參數 ===")
    
    payload = {
        "model": TEST_MODEL,
        "prompt": "hello world test"
    }
    
    start = time.time()
    r = requests.post(f"{OLLAMA_BASE}/api/embeddings", json=payload, timeout=TIMEOUT)
    elapsed = time.time() - start
    
    print(f"  Endpoint: /api/embeddings")
    print(f"  Payload: model={TEST_MODEL}, prompt='hello world test'")
    print(f"  Status: {r.status_code}")
    print(f"  Time: {elapsed:.3f}s")
    
    data = r.json()
    emb = data.get("embedding", [])
    
    print(f"  Embedding dims: {len(emb)}")
    print(f"  First 5 values: {emb[:5] if emb else 'N/A'}")
    
    if len(emb) > 0:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL - Empty embedding")
        return False

def test_legacy_api_multiple_texts():
    """測試多個文本的 embedding（模擬 embedBatch）"""
    print("\n=== 測試 2: Legacy API + 多個文本 ===")
    
    texts = [
        "今天天氣很好",
        "記憶系統的運作原理",
        "Minecraft 翻譯工具",
        "你好嗎？"
    ]
    
    results = []
    for text in texts:
        payload = {"model": TEST_MODEL, "prompt": text}
        start = time.time()
        r = requests.post(f"{OLLAMA_BASE}/api/embeddings", json=payload, timeout=TIMEOUT)
        elapsed = time.time() - start
        data = r.json()
        emb = data.get("embedding", [])
        results.append({
            "text": text,
            "dims": len(emb),
            "time": elapsed,
            "success": len(emb) > 0
        })
        print(f"  '{text[:20]}...' → dims={len(emb)}, time={elapsed:.3f}s")
    
    all_pass = all(r["success"] for r in results)
    print(f"\n  Results: {sum(r['success'] for r in results)}/{len(results)} passed")
    print(f"  ✅ PASS" if all_pass else "  ❌ FAIL")
    return all_pass

def test_response_format():
    """測試回傳格式轉換（確保轉成 OpenAI 格式）"""
    print("\n=== 測試 3: 回傳格式轉換 ===")
    
    payload = {"model": TEST_MODEL, "prompt": "format test"}
    r = requests.post(f"{OLLAMA_BASE}/api/embeddings", json=payload, timeout=TIMEOUT)
    data = r.json()
    
    # 模擬 embedder.ts 修改後的轉換
    ollama_response = data  # {embedding: [...]}
    openai_format = {"data": [{"embedding": ollama_response["embedding"]}]}
    
    print(f"  Ollama raw: {json.dumps({k: len(v) if isinstance(v, list) else v for k, v in ollama_response.items()})}")
    print(f"  OpenAI format: {json.dumps({k: len(v[0]['embedding']) if k == 'data' and v else v for k, v in openai_format.items()})}")
    
    # 驗證 OpenAI format
    if "data" in openai_format and len(openai_format["data"]) == 1:
        emb = openai_format["data"][0]["embedding"]
        if len(emb) == 768:  # nomic-embed-text 預設 768 dims
            print(f"  ✅ PASS - 格式正確，768 dims")
            return True
    
    print("  ❌ FAIL")
    return False

def test_dimensions_consistency():
    """測試不同文本維度一致性"""
    print("\n=== 測試 4: 維度一致性 ===")
    
    texts = ["a", "hello world", "這是一個很長的中文句子用於測試"] * 3
    
    dims_set = set()
    for text in texts:
        payload = {"model": TEST_MODEL, "prompt": text}
        r = requests.post(f"{OLLAMA_BASE}/api/embeddings", json=payload, timeout=TIMEOUT)
        data = r.json()
        emb = data.get("embedding", [])
        if emb:
            dims_set.add(len(emb))
    
    print(f"  不同文本的維度集合: {dims_set}")
    
    if len(dims_set) == 1:
        print(f"  ✅ PASS - 所有文本維度一致: {dims_set.pop()}")
        return True
    else:
        print(f"  ❌ FAIL - 維度不一致")
        return False

def main():
    print("=" * 60)
    print("Ollama 0.20.5 Embedding 修復方案測試")
    print("=" * 60)
    
    # 檢查 Ollama 是否運行
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/version", timeout=5)
        version = r.json().get("version", "unknown")
        print(f"\nOllama 版本: {version}")
    except Exception as e:
        print(f"\n❌ 無法連接 Ollama: {e}")
        return
    
    results = []
    results.append(("Legacy API + prompt", test_legacy_api_with_prompt()))
    results.append(("多個文本", test_legacy_api_multiple_texts()))
    results.append(("格式轉換", test_response_format()))
    results.append(("維度一致性", test_dimensions_consistency()))
    
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:20s}: {status}")
    
    all_pass = all(passed for _, passed in results)
    
    print()
    if all_pass:
        print("🎉 所有測試通過！修復方案有效")
        print("\n建議修改 embedder.ts 的 embedWithNativeFetch 方法：")
        print("  1. endpoint 改成: baseURL.replace(/\\/v1$/, '') + '/api/embeddings'")
        print("  2. payload 改成: {model, prompt: payload.input}")
        print("  3. 回傳轉換成 OpenAI format: {data: [{embedding: data.embedding}]}")
    else:
        print("⚠️ 有測試失敗，請檢查修復方案")
    
    return all_pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
