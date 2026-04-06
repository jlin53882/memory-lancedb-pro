# Venv 剩餘套件筆記 (1/2)

> 來源：Minecraft_translator_flet venv  
> 路徑：`C:\Users\admin\Desktop\minecraft_translator_flet\.venv\Lib\site-packages`  
> 日期：2026-03-15

---

## 1. annotated_types

**版本**：0.7.0  
**用途**：為型別註解（Annotated）提供可組合的元資料約束，用於 Pydantic 等庫

### 模組結構

```
annotated_types/
├── __init__.py       # 主要匯出
├── test_cases.py     # 測試案例
└── py.typed         # 類型標記
```

### 主要 API

#### 比較約束（Comparison Constraints）

| 類別 | 用途 | 範例 |
|------|------|------|
| `Gt(gt=x)` | 值必須大於 x | `Annotated[int, Gt(0)]` |
| `Ge(ge=x)` | 值必須大於等於 x | `Annotated[int, Ge(0)]` |
| `Lt(lt=x)` | 值必須小於 x | `Annotated[int, Lt(100)]` |
| `Le(le=x)` | 值必須小於等於 x | `Annotated[int, Le(100)]` |

#### 區間約束

```python
Interval(gt=0, lt=100)  # 0 < x < 100
Interval(ge=0, le=100)  # 0 <= x <= 100
```

#### 長度約束

| 類別 | 用途 |
|------|------|
| `MinLen(min_length=n)` | 最小長度 >= n |
| `MaxLen(max_length=n)` | 最大長度 <= n |
| `Len(min_length=n, max_length=m)` | 長度範圍 |

#### 數值類型約束

```python
MultipleOf(multiple_of=3)  # 必須是 3 的倍數
```

#### 字串類型約束

```python
LowerCase    # 小寫字串
UpperCase    # 大寫字串
IsDigits     # 全數字字串
IsAscii      # ASCII 字串
```

#### 數值類型約束

```python
IsFinite    # 有限值（非無限、非 NaN）
IsNan        # NaN 值
IsInfinite  # 無限值
```

#### 其他

```python
Timezone(tz=timezone.utc)  # 時區約束
Predicate(func=...)       # 自訂斷言函數
doc("文件說明")            # 文件註解
```

---

## 2. arrow

**版本**：1.4.0  
**用途**：現代化的日期時間處理庫，提供更友善的 API

### 模組結構

```
arrow/
├── __init__.py      # 主要 API
├── api.py           # 工廠函數 (get, now, utcnow)
├── arrow.py         # Arrow 類別（核心）
├── factory.py       # ArrowFactory 工廠
├── formatter.py    # 格式化常數
├── parser.py       # 解析器
├── locales.py      # 區域設定
├── util.py         # 工具函數
└── constants.py    # 常數
```

### 主要 API

#### 建立 Arrow 物件

```python
import arrow

# 從 datetime 建立
arrow.get(datetime_obj)
arrow.get("2023-01-01")
arrow.get("2023-01-01T12:00:00")

# 取得現在時間
arrow.now()           # 本地時區
arrow.utcnow()        # UTC
arrow.now("US/Pacific")  # 指定時區

# 直接建立
arrow.Arrow(2023, 1, 1, 12, 30, 45)
```

#### Arrow 類別主要方法

```python
# 時間操作
dt.shift(weeks=1)           # 移動時間
dt.replace(hour=12)         # 替換時間
dt.floor("hour")            # 向下取整
dt.ceil("hour")             # 向上取整

# 格式化
dt.format("YYYY-MM-DD")
dt.humanize()               # 人類可讀格式 ("2 hours ago")

# 時區轉換
dt.to("US/Pacific")
dt.to("UTC")

# 相對時間
dt.shift(days=+1)
dt.shift(hours=-2)
```

#### 格式常數

```python
FORMAT_ATOM      # ISO 8601
FORMAT_RFC2822   # RFC 2822
FORMAT_RFC3339   # RFC 3339
FORMAT_COOKIE    # HTTP Cookie
FORMAT_RFC822    # RSS/RFC 822
```

---

## 3. binaryornot

**版本**：0.4.4  
**用途**：判斷檔案是二進制還是文字檔

### 模組結構

```
binaryornot/
├── __init__.py      # 版本資訊
├── check.py         # 主邏輯
└── helpers.py        # 輔助函數
```

### 主要 API

```python
from binaryornot.check import is_binary

# 判斷檔案是否為二進制
is_binary("file.txt")   # False
is_binary("image.png")  # True
is_binary("data.bin")   # True
```

#### 演算法原理

1. **副檔名檢查**：已知二進制副檔名（如 `.pyc`）
2. **控制字元比例**：ASCII 控制字元 > 30% 視為二進制
3. **高位元組檢查**：高位 ASCII 字元 < 5% 視為二進制
4. **編碼檢測**：使用 `chardet` 檢測是否可解碼為文字

---

## 4. cachetools

**版本**：6.2.4  
**用途**：可擴展的記憶化集合和裝飾器

### 模組結構

```
cachetools/
├── __init__.py       # 主要類別和裝飾器
├── keys.py          # 金鑰函數
├── func.py          # 函式工具
├── _cached.py       # 快取裝飾器實作
└── _cachedmethod.py # 方法快取實作
```

### 主要類別

| 類別 | 用途 | 淘汰策略 |
|------|------|----------|
| `Cache` | 基礎快取類別 | 無 |
| `FIFOCache` | FIFO 先進先出 | 最早進入 |
| `LRUCache` | LRU 最近最少使用 | 最久未使用 |
| `LFUCache` | LFU 最少頻率使用 | 使用頻率最低 |
| `RRCache` | Random Replacement | 隨機淘汰 |
| `TTLCache` | TTL 過期時間 | 依時間過期 |
| `TLRUCache` | Time-aware LRU | 時間感知 LRU |

### 使用範例

```python
from cachetools import LRUCache, cached

# 直接使用
cache = LRUCache(maxsize=100)
cache["key"] = "value"
value = cache["key"]

# 裝飾器
from cachetools import cached

@cached(cache=LRUCache(maxsize=128))
def expensive_function(x):
    return x * x

# 取得快取資訊
expensive_function.cache_info()
# CacheInfo(hits=0, misses=1, maxsize=128, currsize=1)
```

### 類別比較

| 類別 | 特性 |
|------|------|
| `Cache(maxsize, getsizeof)` | 基礎類別，可自訂大小計算 |
| `FIFOCache(maxsize)` | 簡單佇列 |
| `LRUCache(maxsize)` | 常用，效能好 |
| `LFUCache(maxsize)` | 考慮使用頻率 |
| `TTLCache(maxsize, ttl)` | 時間基礎過期 |
| `TLRUCache(maxsize, ttu)` | 自訂時間到期的函數 |

---

## 5. chardet

**版本**：5.2.0  
**用途**：字元編碼偵測庫

### 模組結構

```
chardet/
├── __init__.py              # 主要 API
├── universaldetector.py     # 通用偵測器
├── detect.py                # 偵測函數
├── resultdict.py            # 結果字典
├── version.py               # 版本資訊
├── cli/                     # 命令列工具
├── *.pyprober.py           # 各種編碼偵測器
└── lang*.py                # 語言模型
```

### 主要 API

```python
import chardet

# 偵測單一編碼
result = chardet.detect(b"Hello World")
# {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}

# 偵測多位編碼
results = chardet.detect_all(b"Hello World")
# [{'encoding': 'ascii', 'confidence': 1.0, 'language': ''}]

# 使用 UniversalDetector
detector = chardet.UniversalDetector()
for line in file:
    detector.feed(line)
detector.close()
result = detector.result
```

#### ResultDict 結構

```python
{
    'encoding': 'utf-8',    # 編碼名稱
    'confidence': 0.99,     # 信心度 0-1
    'language': 'en'        # 語言
}
```

#### 支援的編碼

- UTF-8 / UTF-16 / UTF-32
- ISO-8859 系列 (Latin-1, Latin-2...)
- Windows-125x
- Big5, GB2312, EUC-KR, Shift_JIS
- 與更多...

---

## 6. colorama

**版本**：0.4.6  
**用途**：終端機彩色輸出，跨平台 ANSI 色彩支援

### 模組結構

```
colorama/
├── __init__.py        # 主要匯出
├── ansi.py            # ANSI 程式碼常數
├── ansitowin32.py    # Windows 轉換
├── initialise.py     # 初始化
├── win32.py          # Windows API
├── winterm.py        # Windows 終端機
└── tests/           # 測試
```

### 主要 API

```python
from colorama import Fore, Back, Style, init

# 初始化（Windows 需要）
init(autoreset=True)

# 前景色
print(Fore.RED + "紅色文字")
print(Fore.GREEN + "綠色文字")
print(Fore.BLUE + "藍色文字")

# 背景色
print(Back.YELLOW + "黃色背景")

# 樣式
print(Style.BRIGHT + "亮色")
print(Style.DIM + "暗淡")
print(Style.RESET_ALL + "重置")

# 常用顏色
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
Style: DIM, NORMAL, BRIGHT, RESET_ALL, RESET_BRIGHT, RESET_DIM

# 簡化用法
print(Back.RED + Fore.WHITE + "錯誤訊息" + Style.RESET_ALL)
```

### 快捷函數

```python
from colorama import just_fix_windows_console

# 快速修復 Windows 控制台（不需要完整 init）
just_fix_windows_console()
```

---

## 7. dateutil

**版本**：2.9.0.post0  
**用途**：日期時間工具增強庫

### 模組結構

```
dateutil/
├── __init__.py         # 懶惰載入
├── relativedelta.py    # 相對時間增量
├── parser.py           # 日期字串解析
├── rrule.py           # 循環規則
├── easter.py          # 復活節計算
├── tz/                # 時區
├── tzwin.py          # Windows 時區
├── zoneinfo.py       # IANA 時區資料
└── utils.py          # 工具函數
```

### 主要 API

#### relativedelta - 相對時間

```python
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

from datetime import datetime, timedelta

now = datetime.now()

# 相對增量
delta = relativedelta(years=1, months=2, days=3)
result = now + delta

# 兩個日期之間的差異
delta = relativedelta(datetime(2023, 5, 1), datetime(2023, 1, 1))
# delta.years, delta.months, delta.days

# 週 weekday (MO = Monday, TU = Tuesday, ...)
next_monday = now + relativedelta(weekday=MO)
first_monday = now + relativedelta(day=1, weekday=MO(1))
```

#### parser - 日期解析

```python
from dateutil import parser

# 自動解析日期字串
parser.parse("2023-01-01")
parser.parse("Jan 1, 2023")
parser.parse("01/01/2023")
parser.parse("tomorrow")
parser.parse("next Friday")

# 指定資訊
parser.parse("2023-01-01", dayfirst=True)  # 日在前
parser.parse("01/01/2023", yearfirst=True) # 年在前
```

#### rrule - 循環規則

```python
from dateutil.rrule import rrule, WEEKLY, MONTHLY
from datetime import datetime

# 每週五
for dt in rrule(freq=WEEKLY, byweekday=FR, dtstart=datetime(2023,1,1)):
    print(dt)

# 每月第一天
for dt in rrule(freq=MONTHLY, bymonthday=1, dtstart=datetime(2023,1,1)):
    print(dt)
```

#### tz / zoneinfo - 時區

```python
from dateutil import tz
from dateutil.zoneinfo import get_zoneinf

# 取得時區
tz.gettz("Asia/Taipei")     # 台灣時區
tz.gettz("UTC")             # UTC
tz.gettz("US/Eastern")      # 美國東部

# IANA 時區資料
zone = get_zoneinf("Asia/Taipei")

# 本地時區
tz.get_localizer().localize(dt, is_dst=False)
```

#### easter - 復活節

```python
from dateutil.easter import easter

easter(2023)    # datetime.date(2023, 4, 9)
easter(2024)    # datetime.date(2024, 3, 31)
```

---

## 總結

| 套件 | 版本 | 主要用途 |
|------|------|----------|
| annotated_types | 0.7.0 | 型別註解約束（Pydantic 相容） |
| arrow | 1.4.0 | 現代化日期時間處理 |
| binaryornot | 0.4.4 | 偵測檔案類型（二進制/文字） |
| cachetools | 6.2.4 | 快取裝飾器和集合 |
| chardet | 5.2.0 | 字元編碼偵測 |
| colorama | 0.4.6 | 終端機彩色輸出 |
| dateutil | 2.9.0 | 日期時間增強工具 |

---

*筆記持續更新中...*
