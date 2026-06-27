"""Convert equation image regions to LaTeX (gracefully handles missing torch)."""
from PIL import Image

try:
    from pix2tex.cli import LatexOCR
    _PIX2TEX_AVAILABLE = True
except Exception:
    _PIX2TEX_AVAILABLE = False


class LatexConverter:
    """Wraps pix2tex; raises if not available so pipeline can skip gracefully."""

    def __init__(self):
        if not _PIX2TEX_AVAILABLE:
            raise RuntimeError("pix2tex unavailable (likely torch DLL issue)")
        self.model = LatexOCR()

    def convert(self, image: Image.Image) -> str:
        try:
            return self.model(image)
        except Exception as exc:
            return f"% lens-ocr error: {exc}"
