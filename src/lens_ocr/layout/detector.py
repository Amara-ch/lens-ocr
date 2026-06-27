"""Layout detection using Surya — detects titles, tables, figures, equations, etc."""
from typing import List, Dict, Any
from PIL import Image

from surya.layout import batch_layout_detection
from surya.model.detection.model import load_model, load_processor
from surya.settings import settings


class LayoutDetector:
    """Detects structured regions in a document page."""

    def __init__(self):
        # Layout model (region classification)
        self.model = load_model(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)
        self.processor = load_processor(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)
        # Text-line detection model (Surya requires this internally)
        self.det_model = load_model()
        self.det_processor = load_processor()

    def detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Return list of {type, bbox, confidence} dicts."""
        predictions = batch_layout_detection(
            [image],
            self.model,
            self.processor,
            self.det_model,
            self.det_processor,
        )

        regions: List[Dict[str, Any]] = []
        for pred in predictions:
            for box in pred.bboxes:
                regions.append({
                    "type": box.label.lower(),
                    "bbox": (
                        int(box.bbox[0]),
                        int(box.bbox[1]),
                        int(box.bbox[2]),
                        int(box.bbox[3]),
                    ),
                    "confidence": float(getattr(box, "confidence", 0.95)),
                })
        return regions