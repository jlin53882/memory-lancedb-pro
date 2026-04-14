import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

prompt = """你是對抗式 code reviewer。請分析以下 minecraft_translator_flet 專案中的 11 個 CRITICAL 安全與邏輯問題。

## 請分析的檔案與問題

### C-1：lm_translator_shared_loop.py
代碼：
# C-1 修復：使用原始批次大小切片，而非實際處理的數量
expected = len(batch)
if actual_processed_in_this_batch < expected:
    log_info(f'[SharedLM] API 回傳數量低於預期...')
remaining = remaining[expected:]
問題：若翻譯 API 回傳數量多於 batch_size，會發生什麼？

### C-2：lm_api_client.py
代碼：
max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.post(url, headers=headers, json=data, timeout=request_timeout)
        if not response.ok:
            raise requests.HTTPError(...)
        break
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        last_exception = e
        if attempt < max_retries - 1:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
            continue
        raise
問題：HTTP 429 Rate Limit 會被正確處理嗎？會无限 retry 嗎？

### C-3：lm_translator_main.py
代碼：
marked_batch = []
for item in current_batch:
    marked_item = dict(item)
    marked_item['_untranslated'] = True
    marked_batch.append(marked_item)
all_results.extend(marked_batch)
問題：caller 是否真的會檢查 _untranslated 標記？

### C-4：jar_processor_extract.py
代碼：
abs_output = os.path.abspath(final_output_path)
abs_root = os.path.abspath(output_root)
if not abs_output.startswith(abs_root + os.sep) and abs_output != abs_root:
    log_warning(f'路徑遍歷攻擊偵測')
    continue
問題：所有路徑都通過此檢查了嗎？

### C-5~C-10：ZIP bomb 保護
- lang_merge_zip_io.py：50MB 上限 + 限速讀取
- jar_browser.py：10MB 文字檔上限
- icon_index.py：10MB lang 檔上限
- icon_preview_view.py：512KB icon、10MB model、10MB toml 上限
- lang_merge_content_copy.py
問題：這些保護是否真的有效？

### C-11：cache_shards.py
代碼：
no_progress_count = 0
while pending_items:
    ...
    if len(chunk) == 0:
        no_progress_count += 1
        if no_progress_count >= 3:
            break
    else:
        no_progress_count = 0
問題：no_progress_count 機制是否完整？有其他無限迴圈情境嗎？

## 輸出格式
對 C-1 到 C-11：
1. 風險評估：✅ 已修復 / ⚠️ 部分修復 / ❌ 未修復
2. 詳細分析（不超過 100 字）
3. 建議（如果還有問題）
"""

result = run_opencode_task(prompt=prompt, model="minimax/MiniMax-M2.7", reasoning="high")
print(result)
