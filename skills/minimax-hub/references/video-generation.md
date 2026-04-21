# 影片生成（Video Generation）

> 使用 `video_generate` tool 呼叫 MiniMax-Hailuo-2.3 模型。
> 支援文生視頻、圖生視頻、首尾幀視頻、主體參考視頻。

---

## 支援模型

| 模型 | 說明 |
|------|------|
| **MiniMax-Hailuo-2.3** | 最新旗艦模型，預設 5 秒 720P |

### 舊版模型（仍可用）

- MiniMax-Hailuo-2.0
- MiniMax-Hailuo-2.1

---

## 支援比例

| 比例 | 說明 |
|------|------|
| 16:9 | 橫向（預設） |
| 9:16 | 縱向（短影片） |
| 1:1 | 方形 |

---

## 解析度

| 解析度 | 說明 |
|--------|------|
| 480P | 標清 |
| 720P | 預設高清 |
| 768P | 高清+ |
| 1080P | 全高清 |

---

## 影片類型

### 1. 文生影片（Text-to-Video）

最基本的影片生成方式。

```javascript
video_generate(
  prompt="鏡頭緩慢推進，一隻橘貓走過雨夜街道，霓虹燈反光"
)
```

### 2. 圖生影片（Image-to-Video）

使用參考圖片作為首幀。

```javascript
video_generate(
  prompt="讓這幅畫動起來，海浪輕輕搖晃",
  image="https://example.com/painting.jpg"
)
// 或使用 first_frame
video_generate(
  prompt="人物從室內走到室外",
  first_frame="https://example.com/indoor.jpg"
)
```

### 3. 首尾幀影片（Frame-to-Frame）

提供起始幀和結束幀，AI 生成過渡動畫。

```javascript
video_generate(
  prompt="花朵緩慢綻放的過程",
  first_frame="https://example.com/bud.jpg",
  last_frame="https://example.com/bloom.jpg"
)
```

### 4. 主體參考影片（Subject Reference）

上傳主體圖片，AI 會保持主體特徵生成動畫。

```javascript
video_generate(
  prompt="讓這個人物揮手打招呼",
  image="https://example.com/person.jpg"
)
```

---

## 參數說明

| 參數 | 必填 | 說明 | 預設值 |
|------|------|------|--------|
| `prompt` | ✅ | 影片描述文字 | - |
| `model` | | 模型 | MiniMax-Hailuo-2.3 |
| `duration_seconds` | | 影片時長（秒） | 5 |
| `resolution` | | 解析度：480P/720P/768P/1080P | 720P |
| `aspectRatio` | | 比例：16:9/9:16/1:1 | 16:9 |
| `image` | | 參考圖片（圖生影片/主體參考） | - |
| `first_frame` | | 首幀圖片 URL | - |
| `last_frame` | | 尾幀圖片 URL | - |
| `audio` | | 是否生成音頻（boolean） | - |
| `watermark` | | 是否添加浮水印 | - |

---

## 輸出說明

`video_generate` tool 會自動下載影片並回傳本地檔案路徑。
回傳格式包含：
- `path`: 本地檔案路徑
- `url`: 原始 URL（如有的話）
- `duration`: 實際時長

---

## 影片規格

| 項目 | 預設值 |
|------|--------|
| 時長 | 5 秒 |
| 解析度 | 1280×720 (720P) |
| 格式 | MP4 |

---

## 等待時間

影片生成是**非同步**的，需要輪詢狀態。

`video_generate` tool 會等待影片生成完成後再回傳，但最長可能需要數分鐘。
建議：
- 5 秒影片：等待 60-120 秒
- 10 秒影片：等待 120-180 秒

如果超時，tool 會回傳任務 ID，可用於後續查詢。

---

## Prompt 技巧

### 好的 Prompt 範例

```javascript
// 描述場景 + 鏡頭運動
prompt="長鏡頭穿過繁華的城市街道，霓虹燈閃爍，電影感"

// 描述主體 + 動作
prompt="一隻柴犬在草地上奔跑，陽光穿過樹葉"

// 描述氛圍 + 光線
prompt="清晨霧氣朦朧的森林，陽光從樹縫灑落"
```

### 避免

- 太模糊的描述（如「很好看」）
- 互相矛盾的指示
- 超出具體能力的請求

---

## 限制與配額

- 有每日生成配額限制（依訂閱方案）
- 影片 URL 有效期有限不及時下載
- 某些敏感內容可能被拒絕

---

## 實用技巧

1. **縱向影片（9:16）**：適合 TikTok/Instagram Reels/YouTube Shorts
2. **圖生影片**：首幀圖片品質越高越好
3. **主體參考**：主體要清晰、背景不要太複雜
4. **首尾幀**：兩幀差異不要太大，否則過渡可能不自然
