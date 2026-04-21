---
name: minimax-hub
description: >
  MiniMax 媒體生成樞紐（Hub）。使用時機：
  (1) 生成圖片（文生圖、圖生圖）→ 使用 image_generate tool
  (2) 生成影片（文生視頻、首尾幀、 主體參考）→ 使用 video_generate tool
  (3) 生成音樂（純音樂、帶歌詞）→ 使用 music_generate tool
  (4) 語音合成（TTS）→ 使用 tts tool
  (5) 圖片理解/分析 → 使用 image tool
  觸發詞：生成圖片/影片/音樂/語音、分析圖片、圖片理解、MiniMax、MiniMax Hub
---

# MiniMax Hub — 統一媒體生成入口

> 本 skill 是 MiniMax 所有媒體生成能力的統一入口。
> 使用 OpenClaw 內建的 `image_generate`、`video_generate`、`music_generate`、`tts`、`image` tools，
> 不需要額外安裝腳本或 CLI。

---

## 快速參照

| 需求 | Tool | 主要模型 |
|------|------|---------|
| 文生圖 | `image_generate` | image-01, image-01-live |
| 圖生圖 | `image_generate` + image 參數 | image-01 |
| 文生影片 | `video_generate` | MiniMax-Hailuo-2.3 |
| 圖生影片 | `video_generate` + image 參數 | MiniMax-Hailuo-2.3 |
| 主體參考影片 | `video_generate` | MiniMax-Hailuo-2.3 |
| AI 音樂 | `music_generate` | music-2.5 |
| 文字轉語音 | `tts` | speech-2.8-hd |
| 圖片理解 | `image` | MiniMax VLM |

---

## 圖片生成（image_generate）

### 基本用法

```
image_generate(prompt="一隻穿西裝的橘貓，電影感，柔光")
```

### 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `prompt` | 圖片描述（必填） | "一隻可愛的橘貓" |
| `model` | 模型：image-01 / image-01-live | image-01 |
| `aspect_ratio` | 比例：1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9 | 16:9 |
| `resolution` | 解析度：1K / 2K | 2K |
| `count` | 生成數量 1-4 | 2 |
| `image` | 參考圖片（圖生圖） | URL 或本地路徑 |

### 詳細文件
→ `references/image-generation.md`

---

## 影片生成（video_generate）

### 基本用法

```
video_generate(prompt="鏡頭緩慢推進，一隻橘貓走過雨夜街道，霓虹燈反光")
```

### 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `prompt` | 影片描述（必填） | "日出時分的海邊" |
| `model` | 模型 | MiniMax-Hailuo-2.3 |
| `duration_seconds` | 時長（秒） | 5 |
| `resolution` | 480P / 720P / 768P / 1080P | 720P |
| `image` | 首幀圖片（圖生視頻） | URL 或本地路徑 |
| `first_frame` | 首幀 | URL |
| `last_frame` | 尾幀 | URL |
| `aspectRatio` | 比例：16:9, 9:16, 1:1 | 16:9 |

### 詳細文件
→ `references/video-generation.md`

---

## 音樂生成（music_generate）

### 基本用法

```
music_generate(prompt="Piano, Relaxing, Meditative, Soft, Ambient")
```

### 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `prompt` | 音樂風格描述（必填） | "Jazz, Smooth, Saxophone" |
| `lyrics` | 歌詞（帶 [Verse], [Chorus] 標記） | "[Verse]\n..." |
| `instrumental` | 是否純音樂 | true |
| `durationSeconds` | 時長（秒） | 180 |
| `format` | 格式：mp3 / wav | mp3 |

### 詳細文件
→ `references/music-generation.md`

---

## 語音合成（tts）

### 基本用法

```
tts(text="你好，這是語音測試。")
```

### 常用參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `text` | 要轉語音的文字（必填） | - |
| `channel` | 輸出格式 | telegram |

### 詳細文件
→ `references/tts.md`

---

## 圖片理解（image）

### 基本用法

```
image(prompt="詳細描述這張圖片的內容", image="https://example.com/image.jpg")
```

### 詳細文件
→ `references/vision.md`

---

## 模型總覽

→ `references/models.md`

---

## 使用流程

1. **理解需求**：圖片 / 影片 / 音樂 / 語音 / 圖片理解
2. **選擇工具**：對照上方快速參照表
3. **查閱詳細文件**：必要時查看 references/
4. **生成**：直接呼叫對應 tool
5. **交付**：將產出檔案路徑或 URL 回傳給使用者

## 限制與配額

- **image-01**: Coding Plan 用戶可用，具體限制依訂閱方案
- **video (Hailuo-2.3)**: 有每日生成配額限制
- **music-2.5**: Token Plan 方案用戶可用
- **tts (speech-2.8-hd)**: 依 API 用量計費

配額相關問題 → 參考 `references/models.md`
