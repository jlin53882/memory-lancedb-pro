# Minecraft_translator_flet venv 套件學習筆記

> 筆記日期：2026-03-15
> venv 路徑：`C:\Users\admin\Desktop\minecraft_translator_flet\.venv\Lib\site-packages`

---

## 1. pandas (2.3.3)

### 模組結構
```
pandas/
├── api/          # 公開 API 介面
├── arrays/       # 陣列擴展
├── core/         # 核心實作
├── errors/       # 錯誤類別
├── io/           # 輸入輸出 (CSV, Excel, SQL, JSON 等)
├── plotting/     # 繪圖功能
├── tseries/      # 時間序列
└── __init__.py   # 主要匯出
```

### 主要 API

#### 核心資料結構
```python
# Series: 一維標記陣列
Series(data=None, index=None, dtype=None, name=None, copy=False, fastpath=False)

# DataFrame: 二維表格結構
DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
```

#### I/O 函數
```python
# CSV
read_csv(filepath_or_buffer, ...) -> DataFrame
to_csv(path_or_buf, ...) -> str | None

# Excel
read_excel(io, sheet_name=0, ...) -> DataFrame | dict[DataFrame]
ExcelWriter(path, engine=None, ...)  # 寫入 Excel

# JSON
read_json(path_or_buf, ...) -> DataFrame
json_normalize(data, record_path=None, ...) -> DataFrame  # 將巢狀 JSON 攤平

# SQL
read_sql(sql, con, ...) -> DataFrame
read_sql_table(table_name, con, ...) -> DataFrame
read_sql_query(sql, con, ...) -> DataFrame
```

#### 資料處理
```python
# 轉換
to_datetime(arg, ...) -> DatetimeIndex | Timestamp
to_numeric(arg, ...) -> ndarray
to_timedelta(arg, ...) -> Timedelta

# 合併
concat(objs, axis=0, ...) -> DataFrame | Series
merge(left, right, how='inner', on=None, ...) -> DataFrame
merge_asof(left, right, on=None, ...) -> DataFrame
pivot(data, index=None, columns=None, values=None) -> DataFrame
pivot_table(data, values=None, index=None, columns=None, ...) -> DataFrame

# 重塑
melt(df, id_vars=None, value_vars=None, ...) -> DataFrame
wide_to_long(df, stubnames, i, j, ...) -> DataFrame
```

#### 時間序列
```python
date_range(start=None, end=None, periods=None, freq=None, ...) -> DatetimeIndex
bdate_range(start=None, end=None, periods=None, freq='B', ...) -> DatetimeIndex
period_range(start=None, end=None, periods=None, freq=None, ...) -> PeriodIndex
timedelta_range(start=None, end=None, periods=None, freq=None, ...) -> TimedeltaIndex
Timestamp(year, month, day, ...)  # 時間戳記
Timedelta(value, unit=None)         # 時間差
```

#### 類型系統
```python
Int8Dtype(), Int16Dtype(), Int32Dtype(), Int64Dtype()
UInt8Dtype(), UInt16Dtype(), UInt32Dtype(), UInt64Dtype()
Float32Dtype(), Float64Dtype()
StringDtype(), BooleanDtype()
CategoricalDtype(categories=None, ordered=False)
PeriodDtype(freq=None)
IntervalDtype()
DatetimeTZDtype(unit='ns', tz=None)
```

#### 缺失值處理
```python
NA  # 缺失值標記
isna(obj) -> bool | array
isnull(obj) -> bool | array  # 同 isna
notna(obj) -> bool | array
notnull(obj) -> bool | array  # 同 notna
```

#### 選項設定
```python
get_option(key) -> Any
set_option(key, value) -> None
reset_option(key) -> None
describe_option(key) -> str
option_context(key, value): context manager
```

### 重要筆記
- pandas 2.x 需要 `numpy`, `pytz`, `dateutil` 作為硬依賴
- `json_normalize()` 適合將巢狀 JSON 轉換為 DataFrame
- 推薦使用 `pd.read_sql()` 而非直接用 SQLAlchemy

---

## 2. numpy (2.3.4)

### 模組結構
```
numpy/
├── _core/        # 核心 C 擴展
├── lib/          # 通用函數 (histogram, append, etc.)
├── linalg/       # 線性代數
├── fft/          # 傅立葉轉換
├── random/       # 隨機數生成
├── ma/           # 遮罩陣列
├── polynomial/   # 多項式
├── char/         # 字元陣列操作
├── strings/      # 字串操作
└── __init__.py   # 主要匯出
```

### 主要 API

#### 陣列創建
```python
array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0) -> ndarray
arange(start, stop=None, step=1, dtype=None) -> ndarray
empty(shape, dtype=float, order='C') -> ndarray
empty_like(prototype, dtype=None, order='K', subok=True, shape=None) -> ndarray
zeros(shape, dtype=float, order='C') -> ndarray
zeros_like(a, dtype=None, order='K', subok=True, shape=None) -> ndarray
ones(shape, dtype=float, order='C') -> ndarray
full(shape, fill_value, dtype=None, order='C') -> ndarray
full_like(a, fill_value, dtype=None, order='K', subok=True, shape=None) -> ndarray
eye(N, M=None, k=0, dtype=float) -> ndarray  # 單位矩陣
identity(n, dtype=float) -> ndarray
linspace(start, stop, num=50, endpoint=True, retstep=False) -> ndarray
logspace(start, stop, num=50, endpoint=True, base=10.0) -> ndarray
geomspace(start, stop, num=50, endpoint=True) -> ndarray
```

#### 陣列操作
```python
concatenate(arrays, axis=0, out=None) -> ndarray
vstack(tup) -> ndarray  # 垂直堆疊
hstack(tup) -> ndarray  # 水平堆疊
dstack(tup) -> ndarray  # 深度堆疊
split(ary, indices_or_sections, axis=0) -> list[ndarray]
reshape(a, newshape, order='C') -> ndarray
ravel(a, order='C') -> ndarray  # 攤平
transpose(a, axes=None) -> ndarray
squeeze(a, axis=None) -> ndarray  # 移除維度為 1 的軸
```

#### 數學運算
```python
dot(a, b, out=None) -> ndarray  # 點積
inner(a, b, out=None) -> ndarray  # 內積
outer(a, b, out=None) -> ndarray  # 外積
cross(a, b, axisc=-1, axisb=-1, axisc=-1) -> ndarray  # 叉積
matmul(a, b, out=None) -> ndarray  # 矩陣乘法

einsum(subscripts, *operands, optimize=False, ...) -> ndarray  # Einstein Summation
einsum_path(subscripts, *operands, optimize='greedy') -> (path, contractions)

linalg.matrix_power(a, n) -> ndarray
linalg.solve(a, b) -> ndarray
linalg.inv(a) -> ndarray
linalg.det(a) -> ndarray
linalg.eig(a) -> (eigenvalues, eigenvectors)
linalg.svd(a, full_matrices=True) -> (U, S, Vh)
```

#### 統計函數
```python
amin(a, axis=None, out=None, keepdims=NoValue) -> ndarray
amax(a, axis=None, out=None, keepdims=NoValue) -> ndarray
sum(a, axis=None, dtype=None, out=None, keepdims=NoValue) -> ndarray
mean(a, axis=None, dtype=None, out=None, keepdims=NoValue) -> ndarray
std(a, axis=None, dtype=None, out=None, ddof=0, keepdims=NoValue) -> ndarray
var(a, axis=None, dtype=None, out=None, ddof=0, keepdims=NoValue) -> ndarray
median(a, axis=None, out=None, keepdims=NoValue) -> ndarray
percentile(a, q, axis=None, ...) -> ndarray
quantile(a, q, axis=None, ...) -> ndarray
```

#### 排序與搜尋
```python
sort(a, axis=-1, kind=None, order=None) -> ndarray
argsort(a, axis=-1, kind=None, order=None) -> ndarray
argmax(a, axis=None, out=None) -> ndarray
argmin(a, axis=None, out=None) -> ndarray
where(condition, x=None, y=None) -> ndarray
searchsorted(a, v, side='left', sorter=None) -> ndarray
```

#### 類型
```python
# 數值類型
int8, int16, int32, int64
uint8, uint16, uint32, uint64
float16, float32, float64, float128
complex64, complex128, complex256
bool, object, str, bytes

# 類型查詢
dtype(obj, align=False, copy=False) -> dtype
iinfo(type) -> iinfo  # 整數類型資訊
finfo(type) -> finfo  # 浮點類型資訊
```

#### 隨機數生成
```python
random.rand(d0, d1, ...) -> ndarray  # [0, 1) 均勻分布
random.randn(d0, d1, ...) -> ndarray  # 標準常態分布
random.randint(low, high=None, size=None, dtype=int) -> ndarray
random.random(size=None) -> ndarray
random.choice(a, size=None, replace=False, p=None) -> ndarray
random.shuffle(x) -> None
random.permutation(x) -> ndarray
random.normal(loc=0.0, scale=1.0, size=None) -> ndarray
random.uniform(low=0.0, high=1.0, size=None) -> ndarray
```

### 重要筆記
- NumPy 2.x 有重大改變，某些舊屬性被移除
- `np.float` 已棄用，請使用 `np.float64`
- `np.int` 已棄用，請使用 `np.int64` 或 `np.int32`
- `einsum` 是強大的矩陣運算表達式
- NumPy 預設回傳副本而非原位修改

---

## 3. Pillow (12.0.0)

### 模組結構
```
PIL/
├── Image.py          # 核心 Image 類別
├── ImageDraw.py      # 繪圖
├── ImageFilter.py    # 濾鏡
├── ImageFont.py      # 字體
├── ImageEnhance.py   # 增強
├── ImageOps.py       # 圖像操作
├── ImagePalette.py   # 調色板
├── ImageStat.py      # 統計
├── ImageMath.py      # 數學運算
├── ImageMorph.py     # 形態學操作
├── ImageShow.py      # 顯示圖像
├── ImageTk.py        # Tkinter 整合
└── __init__.py       # 主要匯出
```

### 主要 API

#### 圖像開啟與保存
```python
# 開啟
Image.open(fp, mode='r', formats=None) -> Image

# 儲存
Image.save(fp, format=None, **params) -> None
Image.Image.save(self, fp, format=None, ...) -> None

# 轉換
Image.convert(mode=None, matrix=None, dither=None, palette=0, colors=256) -> Image
Image.resize(size, resample=NEAREST, box=None) -> Image
Image.rotate(angle, resample=NEAREST, expand=False, center=None, translate=None) -> Image
Image.transpose(method) -> Image
```

#### 常用 Image 類別方法
```python
# 實例化
Image.new(mode, size, color=0) -> Image
Image.fromarray(obj, mode=None) -> Image

# 屬性
Image.width -> int
Image.height -> int
Image.mode -> str  # 'RGB', 'RGBA', 'L', 'CMYK', etc.
Image.format -> str | None
Image.size -> tuple[int, int]

# 裁剪與黏貼
Image.crop(box=None) -> Image
Image.paste(im, box=None, mask=None) -> None

# 像素操作
Image.getpixel(xy) -> value
Image.putpixel(xy, value) -> None

# 通道操作
Image.split() -> tuple[Image, ...]  # 分離 RGB 通道
Image.merge(mode, bands) -> Image   # 合併通道
Image.getchannel(channel) -> Image  # 獲取單一通道

# 濾鏡與效果
Image.filter(filter) -> Image
ImageEnhance.Color(image) -> ImageEnhance
ImageEnhance.Contrast(image) -> ImageEnhance
ImageEnhance.Brightness(image) -> ImageEnhance
ImageEnhance.Sharpness(image) -> ImageEnhance
```

#### 常數
```python
# 重新採樣濾鏡
Resampling.NEAREST = 0
Resampling.BOX = 4
Resampling.BILINEAR = 2
Resampling.HAMMING = 5
Resampling.BICUBIC = 3
Resampling.LANCZOS = 1

# 翻轉/旋轉
Transpose.FLIP_LEFT_RIGHT = 0
Transpose.FLIP_TOP_BOTTOM = 1
Transpose.ROTATE_90 = 2
Transpose.ROTATE_180 = 3
Transpose.ROTATE_270 = 4
Transpose.TRANSPOSE = 5
Transpose.TRANSVERSE = 6
```

#### 調色板與顏色
```python
ImageColor.getcolor(color, mode) -> tuple
ImageColor.getrgb(color) -> tuple
```

#### 異常
```python
class UnidentifiedImageError(OSError):
    """無法識別或開啟圖像時拋出"""
```

### 重要筆記
- Pillow 12.0.0 是當前最新穩定版
- 載入大圖片時會有 `DecompressionBombWarning`，可設定 `MAX_IMAGE_PIXELS`
- `Image.open()` 不會立即解碼，需要呼叫 `load()` 才會讀取像素資料
- `Image.resize()` 的 `resample` 參數控制插值方式
- 支援 WebP, AVIF, JPEG 2000 等現代圖片格式

---

## 4. orjson (3.11.3)

### 模組結構
```
orjson/
├── __init__.py       # 主要匯出
├── __init__.pyi      # 型別提示
└── orjson.cp312-win_amd64.pyd  # C 擴展
```

### 主要 API

```python
# 序列化 (Python -> JSON)
dumps(obj, *, default=None, option=None, **kwargs) -> bytes
# 預設返回 bytes，不是 str！

# 反序列化 (JSON -> Python)
loads(obj, *, default=None) -> Any
# 支援 str, bytes, bytearray

# 選項 (可組合)
OPT_INDENT_2          # 縮排 2 空格
OPT_SORT_KEYS         # 鍵排序
OPT_NAIVE_UTC         # UTC 時間視為 naive
OPT_UTC_Z             # UTC 時間輸出為 'Z'
OPT_NON_STR_KEYS      # 允許非字串鍵
OPT_OMIT_MICROSECONDS # 省略微秒
OPT_PASSTHROUGH_DATETIME   # 不轉換 datetime
OPT_PASSTHROUGH_DATE       # 不轉換 date
OPT_PASSTHROUGH_DATACLASS  # 不轉換 dataclass
OPT_PASSTHROUGH_SUBCLASS   # 不轉換子類
OPT_SERIALIZE_DATACLASS    # 序列化 dataclass
OPT_SERIALIZE_NUMPY        # 序列化 numpy 陣列
OPT_SERIALIZE_UUID         # 序列化 UUID
OPT_APPEND_NEWLINE         # 附加換行符

# 異常
JSONDecodeError        # JSON 解析錯誤
JSONEncodeError        # JSON 編碼錯誤
```

### 重要筆記
- **orjson 是最快的 Python JSON 庫**（比標準庫快 10 倍以上）
- `dumps()` 返回 `bytes`，不是 `str`
- 需要設定 `option=orjson.OPT_SORT_KEYS` 才能排序鍵
- 支援 numpy 陣列和 dataclass 直接序列化
- 不支援自定義 `default` 函數以外的擴展方式
- 與標準庫 `json` 不完全相容（返回類型不同）

---

## 5. opencc (0.1.7)

### 模組結構
```
opencc/
├── opencc.py         # OpenCC 類別實作
├── config/           # 轉換設定檔 (.json)
├── dictionary/       # 轉換字典檔 (.txt)
├── __init__.py       # 主要匯出
└── __main__.py       # CLI 入口
```

### 主要 API

```python
class OpenCC:
    def __init__(self, conversion=None):
        """
        :param conversion: 轉換類型
            - 'hk2s': 香港繁體 -> 簡體
            - 's2hk': 簡體 -> 香港繁體
            - 's2t': 簡體 -> 繁體
            - 't2s': 繁體 -> 簡體
            - 's2tw': 簡體 -> 台灣繁體
            - 'tw2s': 台灣繁體 -> 簡體
            - 's2twp': 簡體 -> 台灣繁體（慣用詞）
            - 'tw2sp': 台灣繁體 -> 簡體（慣用詞）
            - 't2hk': 繁體 -> 香港繁體
            - 't2tw': 繁體 -> 台灣繁體
        """
    
    def convert(self, string) -> str:
        """轉換字串"""
    
    def set_conversion(self, conversion) -> None:
        """動態設定轉換類型"""
    
    @property
    def conversion_name(self) -> str:
        """取得轉換名稱"""
```

### 使用範例

```python
from opencc import OpenCC

# 初始化（指定轉換類型）
converter = OpenCC('s2t')  # 簡體 -> 繁體

# 轉換
result = converter.convert("你好世界")  # -> "你好世界" 或 "你好世界"（視轉換規則）

# 動態切換
converter.set_conversion('t2s')  # 切換為 繁體 -> 簡體
```

### 重要筆記
- opencc 使用詞典匹配進行轉換，支援詞彙级别的簡繁轉換
- 內建多種轉換配置，涵蓋不同地區的用字習慣
- 轉換時會保留標點符號和空格
- 支援自定義配置和詞典
- 性能較慢，但轉換品質高

---

## 總結比較

| 套件 | 版本 | 用途 | 筆記 |
|------|------|------|------|
| pandas | 2.3.3 | 資料分析/處理 | 適合表格資料，強大的 I/O 能力 |
| numpy | 2.3.4 | 數值計算 | 底層陣列操作，數學運算 |
| Pillow | 12.0.0 | 影像處理 | 現代格式支援（WebP, AVIF） |
| orjson | 3.11.3 | JSON 序列化 | 高效能，返回 bytes |
| opencc | 0.1.7 | 簡繁轉換 | 詞彙级别轉換，支援多地區 |
