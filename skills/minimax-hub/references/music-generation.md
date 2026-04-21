# 音樂生成（Music Generation）

> 使用 `music_generate` tool 呼叫 MiniMax music-2.5 模型。
> 支援純音樂生成和帶歌詞的歌曲創作。

---

## 支援模型

| 模型 | 說明 |
|------|------|
| **music-2.5** | 旗艦音樂生成模型 |

---

## 參數說明

| 參數 | 必填 | 說明 | 預設值 |
|------|------|------|--------|
| `prompt` | ✅ | 音樂風格描述 | - |
| `lyrics` | | 歌詞文字（帶標記） | - |
| `instrumental` | | 是否純音樂（無人聲） | false |
| `durationSeconds` | | 時長（秒） | - |
| `format` | | 輸出格式：mp3 / wav | mp3 |

---

## 使用範例

### 純音樂（Instrumental）

```javascript
music_generate(
  prompt="Piano, Relaxing, Meditative, Soft, Ambient"
)
```

```javascript
music_generate(
  prompt="Jazz, Smooth, Saxophone, Piano, Night Club",
  durationSeconds=180,
  format="mp3"
)
```

```javascript
music_generate(
  prompt="Electronic, Ambient, Atmospheric, Synthesizer, Chill",
  instrumental=true
)
```

### 帶歌詞的歌曲

```javascript
music_generate(
  prompt="Mandopop, Emotional, Ballad",
  lyrics="[Verse]\n夜深人靜\n思念著你\n[Chorus]\n心中的愛\n永不改變"
)
```

```javascript
music_generate(
  prompt="Pop, Upbeat, Energetic",
  lyrics="[Verse]\nWalking down the street\nFeeling the beat\n[Chorus]\nLet's celebrate tonight"
)
```

---

## 歌詞格式

使用標記區分歌曲結構：

```
[Intro]
（純器樂開場）

[Verse]
主歌歌詞

[Pre-Chorus]
副歌前過渡

[Chorus]
副歌/高潮

[Bridge]
對比段落

[Outro]
結尾
```

### 範例

```
[Intro]
(Piano solo)

[Verse]
陽光灑滿大地
花兒開放
[Pre-Chorus]
這一刻如此美好
[Chorus]
快樂每一天
```

---

## 風格關鍵字參考

### 樂器/類型

| 關鍵字 | 說明 |
|--------|------|
| Piano | 鋼琴 |
| Guitar | 吉他 |
| Orchestra | 管弦樂 |
| Jazz | 爵士 |
| Electronic | 電子 |
| Classical | 古典 |
| Rock | 搖滾 |

### 氛圍

| 關鍵字 | 說明 |
|--------|------|
| Relaxing | 放鬆 |
| Upbeat | 輕快 |
| Epic | 史詩 |
| Melancholic | 憂鬱 |
| Romantic | 浪漫 |
| Cinematic | 電影感 |

### 語言/地區

| 關鍵字 | 說明 |
|--------|------|
| Chinese | 中文 |
| Mandopop | 華語流行 |
| K-pop | 韓流 |
| J-pop | 日系流行 |
| Latin | 拉丁 |

---

## 每日配額

| 方案 | 每日生成次數 |
|------|-------------|
| Token Plan 199 | 7 次/天 |
| 其他方案 | 依訂閱方案 |

> 配額每日午夜重置。

---

## 輸出說明

`music_generate` tool 會自動下載音樂並回傳本地檔案路徑。
回傳格式包含：
- `path`: 本地檔案路徑
- `url`: 原始 URL（如有的話）
- `duration`: 實際時長

---

## 實用技巧

1. **純音樂 Prompt**：盡量具體描述想要的氛圍和樂器組合
2. **歌曲 Prompt**：選擇與歌詞情感匹配的風格
3. **時長**：敘事類歌曲建議 180-240 秒，短片段 60-120 秒
4. **及時下載**：音頻 URL 有效期有限

---

## 格式與品質

| 參數 | 選項 | 說明 |
|------|------|------|
| format | mp3 | 預設，通用性好 |
| format | wav | 無損，檔案較大 |
| format | flac | 無損壓縮 |

建議一般用途使用 mp3 即可。

---

## 限制與配額

- **每日配額**：7 次/天（依方案）
- **時長上限**：依 prompt 而定
- **歌詞長度**：建議不超過 500 字
