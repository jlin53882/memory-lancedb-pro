# Minecraft 翻譯專案依賴套件學習筆記

> 學習日期：2026-03-15
> 專案目錄：C:\Users\admin\Desktop\minecraft_translator_flet

---

## 📦 主題一：翻譯與文本處理

### 1.1 opencc（簡繁轉換）

```python
import opencc

# 建立轉換器
converter = opencc.OpenCC('s2t')  # 簡體 → 繁體
# 可用配置：s2t, t2s, s2tw, tw2s, hk2s, s2hk 等

# 轉換文字
result = converter.convert("简体中文")  # → "簡體中文"
```

**注意**：
- 配置文件在 `opencc/config/` 目錄
- 轉換是基於詞典的最長匹配

### 1.2 ftb_snbt_lib（NBT 標籤解析）

```python
from ftb_snbt_lib import parse, tag, write

# 解析 NBT 字串
parsed = parse('{Id:"minecraft:stone",Count:1}')

# 讀取值
print(parsed['Id'])  # "minecraft:stone"

# 寫回 NBT 字串
output = write(parsed)  # '{Id:"minecraft:stone",Count:1}'
```

### 1.3 markdown_it（Markdown 解析）

```python
import markdown_it

md = markdown_it.MarkdownIt()
result = md.render("# Hello\n\n**bold**")
```

---

## 🌐 主題二：HTTP 與網路請求

### 2.1 requests（同步 HTTP）

```python
import requests

# GET 請求
r = requests.get('https://api.example.com/data')
print(r.status_code)
print(r.json())
print(r.text)

# POST 請求
payload = {'key': 'value'}
r = requests.post('https://api.example.com/post', data=payload)

# 帶參數
params = {'q': 'search'}
r = requests.get('https://api.example.com/search', params=params)

# 設定 Header
headers = {'User-Agent': 'MyApp/1.0'}
r = requests.get(url, headers=headers)

# 超時
r = requests.get(url, timeout=10)
```

### 2.2 httpx（同步/異步 HTTP）

```python
import httpx

# 同步用法（類似 requests）
client = httpx.Client()
r = client.get('https://api.example.com/data')

# 異步用法
import httpx

async def fetch():
    async with httpx.AsyncClient() as client:
        r = await client.get('https://api.example.com/data')

# 異步並行
import asyncio
async def fetch_all():
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
```

### 2.3 urllib3（requests 底層）

```python
import urllib3

pool = urllib3.PoolManager()
r = pool.request('GET', 'https://api.example.com/')
```

---

## 📊 主題三：數據處理

### 3.1 pandas（數據分析）

```python
import pandas as pd

# 讀取 CSV
df = pd.read_csv('data.csv')

# 讀取 Excel
df = pd.read_excel('data.xlsx')

# 讀取 JSON
df = pd.read_json('data.json')

# 讀取 Parquet
df = pd.read_parquet('data.parquet')

# 寫出
df.to_csv('output.csv', index=False)
df.to_excel('output.xlsx', index=False)
df.to_json('output.json', orient='records')

# 基本操作
df.head()           # 前 5 行
df.columns          # 欄位名稱
df['column']        # 取得欄位
df.loc[0]           # 取得列
df.dropna()         # 移除空值
df.fillna(value)    # 填充空值
df.merge(other, on='key')  # 合併
df.groupby('col').sum()    # 分組匯總
```

### 3.2 numpy（數值計算）

```python
import numpy as np

# 建立陣列
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# 常用函數
np.mean(arr)       # 平均值
np.sum(arr)       # 總和
np.max(arr)       # 最大值
np.min(arr)       # 最小值
np.std(arr)       # 標準差

# 陣列操作
arr.reshape(2, 3)  # 改變形狀
arr.flatten()     # 攤平
np.concatenate([arr1, arr2])  # 串接
```

---

## 🖼️ 主題四：圖像處理

### 4.1 Pillow（PIL）

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 開啟圖片
img = Image.open('photo.jpg')

# 基本屬性
print(img.size)    # (width, height)
print(img.mode)   # RGB, RGBA, L, etc.
print(img.format) # JPEG, PNG, etc.

# 轉換格式
img = img.convert('RGB')
img = img.resize((800, 600), Image.LANCZOS)
img = img.thumbnail((200, 200))  # 維持比例

# 裁剪
cropped = img.crop((0, 0, 100, 100))  # (left, top, right, bottom)

# 旋轉/翻轉
rotated = img.rotate(90)
flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

# 濾鏡
blurred = img.filter(ImageFilter.BLUR)
sharpened = img.filter(ImageFilter.SHARPEN)

# 繪圖
draw = ImageDraw.Draw(img)
draw.rectangle([(10, 10), (100, 100)], outline='red')
draw.text((10, 10), 'Hello', fill='white')

# 儲存
img.save('output.png', 'PNG')
img.save('output.jpg', 'JPEG', quality=95)

# 建立新圖片
new_img = Image.new('RGB', (500, 500), 'white')
```

---

## 📖 主題五：維基百科查詢

### 5.1 wikipedia

```python
import wikipedia

# 設定語言
wikipedia.set_lang('zh')  # 中文
wikipedia.set_lang('en')  # 英文

# 搜尋
results = wikipedia.search('python', results=10)

# 取得摘要
summary = wikipedia.summary('Python (programming language)', sentences=2)

# 取得完整頁面
page = wikipedia.page('Python (programming language)')
print(page.title)
print(page.content)       # 全文
print(page.url)          # 連結
print(page.images)       # 圖片列表
print(page.links)        # 外部連結

# 速率限制
wikipedia.set_rate_limiting(rate_limit=True)

# 設定 User-Agent
wikipedia.set_user_agent('MyApp/1.0 (my@email.com)')
```

---

## 📄 主題六：檔案處理

### 6.1 pyyaml（YAML）

```python
import yaml

# 讀取 YAML
with open('config.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# 寫入 YAML
with open('output.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True)

# 安全讀取（避免執行惡意代碼）
data = yaml.safe_load(string)

# Loader/Dumper 選項
yaml.safe_load()      # 安全
yaml.full_load()      # 完整（可能不安全）
yaml.dump(data, Dumper=yaml.SafeDumper)
```

### 6.2 json（包括 orjson）

```python
import json

# 標準庫
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False, indent=2)

# orjson（更快）
import orjson

data = orjson.loads(json_bytes)
json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS)
```

---

## 🧪 主題七：測試

### 7.1 pytest

```python
# 執行測試
pytest tests/              # 執行所有測試
pytest tests/test_*.py     # 執行特定檔案
pytest -v                 # 詳細輸出
pytest -k "test_name"     # 只執行名稱包含 test_name 的測試
pytest --collect-only     # 列出所有測試

# 基本測試
def test_example():
    assert 1 + 1 == 2

# 使用 Fixtures
@pytest.fixture
def sample_data():
    return {'key': 'value'}

def test_with_fixture(sample_data):
    assert sample_data['key'] == 'value'

# 參數化
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
])
def test_double(input, expected):
    assert input * 2 == expected
```

---

## 🔧 主題八：其他常用工具

### 8.1 tqdm（進度條）

```python
from tqdm import tqdm

for i in tqdm(range(100), desc="Processing"):
    # 做任務
    pass

# 配合 pandas
df.progress_apply(func)
```

### 8.2 python-dotenv（環境變數）

```python
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 檔案
import os
api_key = os.getenv('API_KEY')
```

### 8.3 arrow（日期時間）

```python
import arrow

now = arrow.now()
print(now.format('YYYY-MM-DD HH:mm:ss'))
print(now.shift(days=1).humanize())

# 解析
dt = arrow.get('2024-01-15 12:00:00')
```

### 8.4 tenacity（重試機制）

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def fetch_data():
    return requests.get(url)
```

---

## ⚠️ 常見陷阱

1. **opencc**：轉換配置名稱要正確（s2t, t2s, s2tw 等）
2. **requests**：記得處理 timeout
3. **pandas**：讀取大型 CSV 時注意記憶體
4. **Pillow**：圖片 RGBA 轉 RGB 要先墊底
5. **wikipedia**：設定正確的語言和 rate limiting
6. **yaml**：用 safe_load 避免安全問題

---

## 📋 驗證指令

```python
# 檢查版本
import flet; print(flet.__version__)
import opencc; print(opencc.__version__)
import PIL; print(PIL.__version__)
import pandas; print(pandas.__version__)
import requests; print(requests.__version__)
import wikipedia; print(wikipedia.__version__)

# 快速測試
import opencc
c = opencc.OpenCC('s2t')
print(c.convert('测试'))  # 應該輸出「測試」
```
