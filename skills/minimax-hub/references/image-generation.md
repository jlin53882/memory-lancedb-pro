# 圖片生成（Image Generation）

> 使用 `image_generate` tool 呼叫 MiniMax image-01 / image-01-live 模型。

---

## 支援模型

| 模型 | 說明 | 支援比例 |
|------|------|---------|
| **image-01** | 畫面表現細膩，支援文生圖、圖生圖 | 全部比例 |
| **image-01-live** | 手繪、卡通等畫風增強 | 部分比例 |

### image-01 vs image-01-live

- **image-01**: 通用場景，畫質細膩真實
- **image-01-live**: 適合動漫/手繪風格，有額外 style 參數

---

## 支援比例

| 比例 | 尺寸（1K） | 尺寸（2K） |
|------|-----------|-----------|
| 1:1 | 1024×1024 | 2048×2048 |
| 16:9 | 1280×720 | 2560×1440 |
| 4:3 | 1152×864 | 2304×1728 |
| 3:2 | 1248×832 | 2496×1664 |
| 2:3 | 832×1248 | 1664×2496 |
| 3:4 | 864×1152 | 1728×2304 |
| 9:16 | 720×1280 | 1440×2560 |
| 21:9 | 1344×576 | 2688×1152 ⚠️ 僅 image-01 |

---

## 參數說明

| 參數 | 必填 | 說明 | 預設值 |
|------|------|------|--------|
| `prompt` | ✅ | 圖片描述文字 | - |
| `model` | | 模型：image-01 / image-01-live | image-01 |
| `aspect_ratio` | | 比例：1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9 | 1:1 |
| `resolution` | | 解析度：1K / 2K | 1K |
| `count` | | 生成數量（1-4） | 1 |
| `image` | | 參考圖片 URL 或本地路徑（圖生圖） | - |
| `filename` | | 輸出檔案名稱提示 | - |

---

## 使用範例

### 文生圖（基本）

```javascript
image_generate(prompt="一隻穿西裝的橘貓，電影感，柔光，寫實風格")
```

### 指定比例

```javascript
image_generate(
  prompt="海邊日落，橙紅色天空，倒影",
  aspect_ratio="16:9",
  resolution="2K"
)
```

### 圖生圖（image-to-image）

```javascript
image_generate(
  prompt="將這張照片轉換成水彩畫風格",
  image="https://example.com/photo.jpg",
  model="image-01"
)
```

### image-01-live 漫畫風

```javascript
image_generate(
  prompt="一個穿著漢服的少女，精緻五官",
  model="image-01-live",
  aspect_ratio="3:4"
)
```

---

## 輸出說明

`image_generate` tool 會自動下載圖片並回傳本地檔案路徑。
回傳格式包含：
- `path`: 本地檔案路徑
- `url`: 原始 URL（如有的話）
- `size_bytes`: 檔案大小

---

## image-01-live 畫風參數（可能不稳定）

> ⚠️ style 參數目前可能不稳定，建議先用預設設定測試。

可用畫風：
- `realistic` — 寫實
- `animation` — 動畫
- `comic` — 漫畫
- `watercolor` — 水彩
- `oil_painting` — 油畫
- `sketch` — 素描
- `cartoon` — 卡通
- `hand_drawn` — 手繪

---

## 限制與配額

- **n 參數**：取值範圍 [1, 9]
- **自訂尺寸**：範圍 [512, 2048]，必須是 8 的倍數
- **URL 有效期**：回傳的 URL 有效期為 24 小時
- **圖生圖**：使用 `image` 參數指定輸入圖片 URL

---

## 實用技巧

1. **比例選擇**：
   - 社群媒體發文 → 1:1 或 16:9
   - 手機背景 → 9:16
   - 橫幅廣告 → 21:9

2. **Prompt 技巧**：
   - 加入風格關鍵字：寫實、動漫、水彩、油畫
   - 加入光線描述：柔光、逆光、霓虹
   - 加入構圖：特寫、廣角、鳥瞰

3. **圖生圖**：
   - 參考圖片建議使用高解析度
   - Prompt 描述你想保留/改變的元素
