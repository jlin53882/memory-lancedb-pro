---
name: minimax-media
description: 使用 MiniMax API 進行圖片生成與文字轉語音（TTS）。支援 image-01 模型生成圖片，以及 speech-2.8-hd 模型生成語音。需要的話再閱讀，不想用時跳過。
homepage: https://platform.minimax.io
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["python"]}}}
---

# MiniMax Media（圖片生成 + 語音）

使用 `python scripts/minimax_media.py` 呼叫。

## 圖片生成

```bash
python scripts/minimax_media.py image "一隻可愛的貓"
```

回傳：`{"image_path": "...", "url": "...", "size_bytes": ...}`

## 語音生成

```bash
python scripts/minimax_media.py tts "你好，這是語音測試。" --voice female-tianmei --speed 1.0
```

可用 `--voice` 參數：
- `female-tianmei`（預設，中文女聲）
- `male-qn-qingse`（中文男聲）
- `male-qn-jianbin`（中文男聲2）
- `English_expressive_narrator`（英文）

可用 `--speed`：0.5 ~ 2.0（預設 1.0）

回傳：`{"audio_path": "...", "size_bytes": ..., "duration_hint": "..."}`

## 注意

- 需要 MINIMAX_API_KEY 環境變數（已有）
- Python 路徑：`C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe`
- 完整路徑：`C:\Users\admin\.openclaw\workspace\skills\minimax-media\scripts\minimax_media.py`
