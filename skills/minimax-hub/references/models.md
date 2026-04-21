# 模型總覽（Quick Reference）

> MiniMax 所有可用模型的快速查詢表。

---

## 圖片生成

| 模型 | 用途 | 比例支援 |
|------|------|---------|
| **image-01** | 文生圖、圖生圖，高畫質 | 全部（8種） |
| **image-01-live** | 手繪、卡通風格增強 | 部分（7種） |

---

## 影片生成

| 模型 | 用途 | 時長 | 解析度 |
|------|------|------|--------|
| **MiniMax-Hailuo-2.3** | 旗艦影片模型 | 5秒（可更長） | 480P-1080P |
| MiniMax-Hailuo-2.1 | 標準影片 | 5秒 | 720P |
| MiniMax-Hailuo-2.0 | 基礎影片 | 5秒 | 720P |

---

## 音樂生成

| 模型 | 用途 | 說明 |
|------|------|------|
| **music-2.5** | AI 音樂生成 | 支援純音樂 + 歌詞歌曲 |

---

## 語音合成（TTS）

| 模型 | 用途 | 特點 |
|------|------|------|
| **speech-2.8-hd** | 高品質語音 | 最高品質，40+語言 |
| **speech-2.8-turbo** | 快速語音 | 低延遲，40+語言 |
| speech-2.6-hd | 高相似度 | 克隆音色等 |
| speech-2.6-turbo | 性價比 | 平衡品質與成本 |

---

## 圖片理解（Vision）

| 模型 | 用途 |
|------|------|
| MiniMax VLM | 圖片理解、分析、OCR |

---

## 配額參考

| 服務 | 配額說明 |
|------|---------|
| image-01 | Coding Plan 用戶可用 |
| video (Hailuo-2.3) | 每日有限配額 |
| music-2.5 | Token Plan 199: 7次/天 |
| tts | 依用量計費 |
| vision | 依用量計費 |

> 具體配額請至 https://platform.minimaxi.com 查詢

---

## API 端點

| 服務 | 端點 |
|------|------|
| 圖片/影片/音樂生成 | `https://api.minimax.io` |
| TTS | `https://api.minimax.io` |
| Vision | 透過 MiniMax MCP 或直接 API |

---

## 模型選擇建議

### 圖片
- 一般用途 → image-01
- 動漫/手繪風 → image-01-live

### 影片
- 最新模型 → MiniMax-Hailuo-2.3
- 快速測試 → MiniMax-Hailuo-2.0

### 音樂
- 目前只有 music-2.5

### 語音
- 最高品質 → speech-2.8-hd
- 低延遲需求 → speech-2.8-turbo
