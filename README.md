# lens-ocr
Open-source document understanding pipeline — OCR, layout detection, equation→LaTeX, structured JSON output
<div align="center">

# 🔎 lens-ocr

### Open-source document understanding pipeline

**Extract text, tables, equations, and layout from any document — into clean structured JSON.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)](api/server.py)

</div>

---

## ✨ Why lens-ocr?

Most OCR tools just dump raw text and lose the structure. **lens-ocr understands documents** — it preserves layout, detects equations, recovers tables, and returns everything as structured JSON ready for RAG pipelines, enterprise search, and downstream AI.

| Feature | lens-ocr | Traditional OCR |
|---|:---:|:---:|
| Text extraction (80+ languages) | ✅ | ✅ |
| Layout detection (titles, tables, figures) | ✅ | ❌ |
| Equation → LaTeX | ✅ | ❌ |
| Table → 2D array | ✅ | ❌ |
| Bounding boxes + confidence per region | ✅ | partial |
| Structured JSON / Markdown output | ✅ | ❌ |
| Self-hosted (Docker) | ✅ | varies |

---

## 🚀 Quick start

### Option A — Python (local)

```bash
git clone https://github.com/Amara-ch/lens-ocr.git
cd lens-ocr
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

lens-ocr parse path/to/document.pdf -o result.json
```

### Option B — Docker

```bash
docker compose up --build
# Then POST a file to http://localhost:8000/parse
```

---

## 📦 What you get

A single JSON output for every document:

```json
{
  "filename": "calculus-exam.pdf",
  "num_pages": 1,
  "processing_time_ms": 5100,
  "regions": [
    {
      "id": "a1b2c3d4",
      "type": "title",
      "bbox": {"x_min": 120, "y_min": 80, "x_max": 540, "y_max": 130},
      "confidence": 0.98,
      "text": "Calculus Final Exam",
      "page": 1
    },
    {
      "id": "e5f6g7h8",
      "type": "equation",
      "bbox": {"x_min": 100, "y_min": 200, "x_max": 480, "y_max": 280},
      "confidence": 0.94,
      "latex": "\\int_0^1 x^2 \\, dx = \\frac{1}{3}",
      "page": 1
    },
    {
      "id": "i9j0k1l2",
      "type": "chart",
      "bbox": {"x_min": 60, "y_min": 320, "x_max": 540, "y_max": 600},
      "confidence": 0.91,
      "page": 1
    }
  ],
  "markdown": "# Calculus Final Exam\n\n$$\n\\int_0^1 x^2 \\, dx = \\frac{1}{3}\n$$\n\n![chart](page-1-region-i9j0k1l2)",
  "plain_text": "Calculus Final Exam"
}
```

---

## 🧩 Architecture

```
┌─────────────────┐
│ Input (PDF/IMG) │
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│ Layout Detector    │  ← Surya  (titles, tables, figures, equations)
└────────┬───────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Region router                              │
│  • text/title   → PaddleOCR                │
│  • equation     → pix2tex (LaTeX)          │
│  • table        → OCR + row grouping       │
│  • figure/chart → bbox preserved           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌──────────────────────────┐
│ DocumentResult (JSON +   │
│ Markdown + plain text)   │
└──────────────────────────┘
```

---

## 💻 CLI usage

```bash
# Basic
lens-ocr parse document.pdf

# JSON output
lens-ocr parse document.pdf -o out.json -f json

# Markdown output
lens-ocr parse document.pdf -o out.md -f markdown

# Non-English (e.g. French)
lens-ocr parse document.pdf -l fr

# GPU acceleration
lens-ocr parse document.pdf --gpu

# Show capabilities
lens-ocr info
```

---

## 🌐 HTTP API

Start the server:

```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Send a file:

```bash
curl -X POST http://localhost:8000/parse \
     -F "file=@document.pdf"
```

Interactive docs: visit `http://localhost:8000/docs`.

---

## 🧠 Tech stack

| Component | Library |
|---|---|
| Layout detection | [Surya](https://github.com/VikParuchuri/surya) |
| Text OCR | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) |
| Equation → LaTeX | [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) |
| API | [FastAPI](https://fastapi.tiangolo.com) |
| CLI | [Typer](https://typer.tiangolo.com) + [Rich](https://github.com/Textualize/rich) |
| Data validation | [Pydantic v2](https://docs.pydantic.dev) |

---

## 🛣️ Roadmap

- [ ] Chart data extraction (axis labels + data points)
- [ ] Signature detection module
- [ ] Multi-column reading-order fix
- [ ] Batch processing API
- [ ] Web UI (drag-and-drop)
- [ ] Fine-tune layout model on custom datasets

---

## 📝 License

MIT © [Amara-ch](https://github.com/Amara-ch)