"""Layout detection using PaddleOCR's PP-Structure (no torch dependency)."""
from typing import List, Dict, Any
import numpy as np
from PIL import Image
from paddleocr import PPStructure


# Map PaddleOCR layout labels to our internal terminology
LABEL_MAP = {
    "title": "title",
    "text": "text",
    "list": "list-item",
    "table": "table",
    "figure": "figure",
    "equation": "equation",
    "header": "page-header",
    "footer": "page-footer",
    "reference": "text",
}


class LayoutDetector:
    """Detects structured regions in a document page using PP-Structure."""

    def __init__(self):
        self.engine = PPStructure(
            table=False,           # we use our own table extractor
            ocr=False,             # we do OCR separately per region
            show_log=False,
            layout=True,
            lang="en",
        )

    def detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Return list of {type, bbox, confidence} dicts."""
        arr = np.array(image)
        if arr.ndim == 3 and arr.shape[2] == 4:
            arr = arr[:, :, :3]  # drop alpha if present

        results = self.engine(arr)

        regions: List[Dict[str, Any]] = []
        for r in results:
            raw_label = r.get("type", "text").lower()
            label = LABEL_MAP.get(raw_label, "text")
            bbox = r.get("bbox", [0, 0, 0, 0])
            regions.append({
                "type": label,
                "bbox": (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
                "confidence": float(r.get("score", 0.9)),
            })

        return regions
