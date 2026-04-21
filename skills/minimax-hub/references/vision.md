# 圖片理解（Vision）

> 使用 `image` tool 呼叫 MiniMax VLM 模型進行圖片理解與分析。

---

## 基本用法

```javascript
image(prompt="詳細描述這張圖片的內容", image="https://example.com/image.jpg")
```

### 本地圖片

```javascript
image(prompt="這張截圖展示了什麼？", image="C:/Users/admin/Desktop/screenshot.png")
```

---

## 參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `prompt` | ✅ | 對圖片的提問或描述要求 |
| `image` | ✅ | 圖片 URL 或本地路徑 |

---

## 使用場景

| 場景 | Prompt 範例 |
|------|------------|
| 描述圖片 | "詳細描述這張圖片的內容" |
| 提取文字 | "請提取圖片中的所有文字" |
| 分析 UI | "描述這個介面的主要元素和佈局" |
| 識別物體 | "圖片中有哪些物體？它們的位置關係是什麼？" |
| 理解圖表 | "請解釋這個圖表的含義和數據趨勢" |
| 識圖翻譯 | "圖片中文字是什麼語言？請翻譯成中文" |

---

## 支援圖片格式

- JPEG
- PNG
- WebP

---

## 多圖分析

```javascript
image(
  prompt="比較這兩張圖片有什麼不同",
  images=[
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
)
```

最多支援 20 張圖片同時分析。

---

## 使用範例

### 截圖分析

```javascript
image(
  prompt="這個網頁截圖的主要內容是什麼？",
  image="C:/Users/admin/Desktop/webpage.png"
)
```

### 產品圖片分析

```javascript
image(
  prompt="描述這個產品的外觀和特點",
  image="https://example.com/product.jpg"
)
```

### 文件掃描

```javascript
image(
  prompt="請識別並提取圖片中的所有文字內容",
  image="https://example.com/document.jpg"
)
```

---

## 限制與用量

- 依 API 用量計費
- 圖片，建議解析度不要過高（浪費 tokens）
- 回傳時間取決於圖片大小和 complexity

---

## 實用技巧

1. **具體提問**：越具體的問題回覆越準確
2. **指定輸出格式**：如「請用條列式說明」
3. **結合其他工具**：分析後可結合生成工具做延伸應用
4. **批量處理**：多張圖片可一次分析
