"""FastAPI HTTP server for lens-ocr."""
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from lens_ocr.pipeline import DocumentPipeline

app = FastAPI(
    title="lens-ocr API",
    description="Document understanding pipeline — OCR, layout, LaTeX, tables.",
    version="0.1.0",
)

# Load pipeline once at startup (models stay in memory)
pipeline: DocumentPipeline | None = None


@app.on_event("startup")
def _load_pipeline():
    global pipeline
    pipeline = DocumentPipeline()


@app.get("/")
def root():
    return {
        "name": "lens-ocr",
        "version": "0.1.0",
        "endpoints": {
            "POST /parse": "Upload a document and get structured JSON",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "pipeline_loaded": pipeline is not None}


@app.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    """Parse an uploaded document (PDF / PNG / JPG)."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready")

    suffix = Path(file.filename or "upload").suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        result = pipeline.process(tmp_path)
        return JSONResponse(content=result.model_dump())
    finally:
        tmp_path.unlink(missing_ok=True)