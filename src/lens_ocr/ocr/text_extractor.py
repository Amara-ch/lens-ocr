"""Text extraction using PaddleOCR (supports 80+ languages)."""
from typing import List, Dict, Any
import numpy as np
from paddleocr import PaddleOCR


class TextExtractor:
    """Wraps PaddleOCR with a simple, normalized output format."""

    def __init__(self, lang: str = "en", use_gpu: bool = False):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False,
        )

    def extract(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run OCR on a numpy image array.

        Returns a list of dicts: {bbox: (x_min, y_min, x_max, y_max), text, confidence}
        """
        result = self.ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []

        extracted: List[Dict[str, Any]] = []
        for line in result[0]:
            bbox_pts, (text, conf) = line
            xs = [p[0] for p in bbox_pts]
            ys = [p[1] for p in bbox_pts]
            extracted.append({
                "bbox": (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))),
                "text": text,
                "confidence": float(conf),
            })
        return extracted
