<div align="center">

# 🔍 lens-ocr

### Mistral-quality OCR — Free, Open Source, runs anywhere.

**Extract clean Markdown with LaTeX equations from any document image — handwritten or printed.**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-lens--ocr.streamlit.app-7f1d1d?style=for-the-badge)](https://lens-ocr.streamlit.app)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://lens-ocr.streamlit.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](api/server.py)
[![Gemini](https://img.shields.io/badge/Gemini_Vision_2.5-4285F4?logo=google&logoColor=white)](https://ai.google.dev)

[**🌐 Try the live demo →**](https://lens-ocr.streamlit.app)

</div>

---

## ✨ What is lens-ocr?

Most OCR tools dump raw text and lose the structure. **lens-ocr understands documents** — it preserves layout, extracts handwritten math as LaTeX, recovers tables as Markdown, and returns clean structured output.

It rivals paid services like Mistral OCR — but it is free, open source, and runs anywhere.

### 📊 Quality comparison

| Feature | Mistral OCR | **lens-ocr** | Traditional OCR |
|---|:---:|:---:|:---:|
| Handwritten math → LaTeX | ✅ | ✅ | ❌ |
| Printed equations → LaTeX | ✅ | ✅ | ❌ |
| Tables → structured Markdown | ✅ | ✅ | ❌ |
| Layout detection | ✅ | ✅ | partial |
| 80+ languages | ✅ | ✅ | ✅ |
| PDFs and images | ✅ | ✅ | ✅ |
| **Cost per page** | $0.05 | **$0** | varies |
| **Open source** | ❌ | ✅ | varies |
| **Self-hostable** | ❌ | ✅ | varies |

---

## 🚀 Three ways to use it

### 1️⃣ Web app — no installation needed

🌐 **[lens-ocr.streamlit.app](https://lens-ocr.streamlit.app)**

Drop an image, click extract, get clean Markdown with LaTeX in 3 seconds. Works in any browser.

### 2️⃣ Command-line tool

```bash
# Install
git clone https://github.com/Amara-ch/lens-ocr.git
cd lens-ocr
pip install -e .

# Get a free Gemini API key: https://aistudio.google.com/apikey
export GEMINI_API_KEY="your-key-here"

# Smart mode (Gemini Vision — Mistral-quality)
lens-ocr smart document.jpg -o output.md

# Local mode (offline, PaddleOCR-based)
lens-ocr parse document.pdf -o output.json
```

### 3️⃣ REST API server

```bash
# Start the server
uvicorn api.server:app --host 0.0.0.0 --port 8000

# Send a file
curl -X POST http://localhost:8000/parse -F "file=@document.pdf"
```

Interactive docs at `http://localhost:8000/docs`.

---

## 🎯 Features

- ✍️ **Handwritten math → LaTeX** — even messy chalkboard scribbles
- 📐 **Printed equations** — fractions, integrals, summations, matrices
- 📊 **Tables → Markdown** — structured row/column extraction
- 📑 **Layout detection** — titles, paragraphs, figures, lists
- 🌍 **80+ languages** — multilingual OCR
- 📄 **PDF and image input** — JPG, PNG, WebP, PDF
- 🔄 **Two modes:**
  - **Smart** — Google Gemini Vision (best quality, needs API key)
  - **Local** — PaddleOCR + pix2tex (offline, no API needed)

---

## 🧠 How it works

### Smart mode (`lens-ocr smart`)

Uses **Google Gemini Vision 2.5** with careful prompt engineering to extract document content into clean Markdown with LaTeX equations.

```
Image ──► Gemini Vision 2.5 ──► Markdown + LaTeX
```

Google's free tier gives you **1,500 requests per day** — more than enough for personal and indie use.

> 🙏 Huge credit to the **Google Gemini team** — the vision model does the heavy lifting. Their generous free tier is what makes this kind of indie tool possible.

### Local mode (`lens-ocr parse`)

Multi-stage pipeline for offline, self-hosted use:

```
┌─────────────────┐
│ Input (PDF/IMG) │
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│ Layout Detector    │  ← PP-Structure  (titles, tables, figures, equations)
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

## 📦 Output format

Local mode returns structured JSON:

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
    }
  ],
  "markdown": "# Calculus Final Exam\n\n$$\n\\int_0^1 x^2 \\, dx = \\frac{1}{3}\n$$",
  "plain_text": "Calculus Final Exam"
}
```

Smart mode returns clean Markdown directly — ready to paste into Notion, Obsidian, GitHub, or any LaTeX-aware editor.

---

## 💻 CLI commands

```bash
# Smart mode (Gemini Vision — Mistral-quality)
lens-ocr smart image.jpg                          # default output
lens-ocr smart image.jpg -o out.md                # custom output
lens-ocr smart image.jpg --model gemini-2.5-pro   # use Pro for highest quality
lens-ocr smart image.jpg --no-html                # skip HTML preview generation

# Local mode (offline)
lens-ocr parse document.pdf                       # basic parse
lens-ocr parse document.pdf -o out.json           # JSON output
lens-ocr parse document.pdf -f markdown -o out.md # Markdown output
lens-ocr parse document.pdf -l fr                 # French OCR

# Info
lens-ocr info                                     # show capabilities
```

---

## 🌐 Run the web app locally

```bash
# Install Streamlit
pip install streamlit google-generativeai pillow

# Set your API key (get one free at aistudio.google.com/apikey)
export GEMINI_API_KEY="your-key-here"      # Linux/Mac
$env:GEMINI_API_KEY = "your-key-here"      # Windows PowerShell

# Run the app
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploy your own instance

Deploy to **Streamlit Cloud** for free in under 5 minutes:

1. **Fork this repo** to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your forked repo
4. **Main file path:** `streamlit_app.py`
5. Click **"Advanced settings"** → **Secrets** tab → paste:
   ```toml
   GEMINI_API_KEY = "your-gemini-key-here"
   ```
6. Click **"Deploy!"**

You'll get a public URL like `https://your-app-name.streamlit.app` in ~3 minutes.

---

## 🛠️ Tech stack

| Component | Technology |
|---|---|
| **Smart OCR model** | [Google Gemini Vision 2.5](https://ai.google.dev) |
| **Web UI** | [Streamlit](https://streamlit.io) |
| **REST API** | [FastAPI](https://fastapi.tiangolo.com) |
| **CLI** | [Typer](https://typer.tiangolo.com) + [Rich](https://github.com/Textualize/rich) |
| **Local layout detection** | [PP-Structure](https://github.com/PaddlePaddle/PaddleOCR) |
| **Local text OCR** | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) |
| **Local equation → LaTeX** | [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) |
| **Data validation** | [Pydantic v2](https://docs.pydantic.dev) |
| **Language** | Python 3.10+ |

---

## 🔐 Security & privacy

- **Your API key is never logged, stored, or shared.** It lives only in environment variables or Streamlit Cloud secrets.
- The hosted demo uses a host-provided Gemini key — your uploaded images are sent to Google's Gemini API for processing only.
- Local mode (`lens-ocr parse`) runs **completely offline** — no data leaves your machine.

---

## 🛣️ Roadmap

- [x] Smart mode with Gemini Vision
- [x] Streamlit web app
- [x] REST API with FastAPI
- [x] CLI tool
- [ ] Multi-page PDF support in smart mode
- [ ] Batch processing API
- [ ] Chart data extraction (axis labels + data points)
- [ ] Signature detection module
- [ ] Multi-column reading-order fix
- [ ] Fine-tune layout model on custom datasets

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Lint
ruff check src/
```

---

## 📝 License

[MIT License](LICENSE) — use it anywhere, modify it freely, ship it commercially.

---

## 🙏 Credits

- **[Google Gemini team](https://ai.google.dev)** — for the brilliant vision model and the genuinely generous free API tier that makes this project possible
- **[Mistral AI](https://mistral.ai)** — for the OCR product that inspired this open-source alternative
- **[PaddleOCR team](https://github.com/PaddlePaddle/PaddleOCR)** — for the rock-solid local OCR engine
- **[Streamlit team](https://streamlit.io)** — for making web app deployment effortless

---

<div align="center">

**Built with ❤️ by [@Amara-ch](https://github.com/Amara-ch)**

If lens-ocr saves you time or money, please consider ⭐ starring the repo!

[🌐 Live Demo](https://lens-ocr.streamlit.app) • [🐛 Report Bug](https://github.com/Amara-ch/lens-ocr/issues) • [💡 Request Feature](https://github.com/Amara-ch/lens-ocr/issues)

</div>
