"""Simple table extractor: OCR within the table region, then group cells into rows."""
from typing import List
import numpy as np
from PIL import Image


class TableExtractor:
    """Heuristic table extractor that groups OCR output by row using Y-proximity."""

    def __init__(self, text_extractor, y_threshold: int = 15):
        self.text_extractor = text_extractor
        self.y_threshold = y_threshold

    def extract(self, image: Image.Image) -> List[List[str]]:
        """Return a 2D list of cell strings."""
        arr = np.array(image)
        cells = self.text_extractor.extract(arr)
        if not cells:
            return []

        # Sort cells top-to-bottom
        cells.sort(key=lambda c: c["bbox"][1])

        rows: List[List[dict]] = []
        current_row: List[dict] = []
        last_y = None

        for c in cells:
            y = c["bbox"][1]
            if last_y is None or abs(y - last_y) <= self.y_threshold:
                current_row.append(c)
            else:
                rows.append(sorted(current_row, key=lambda x: x["bbox"][0]))
                current_row = [c]
            last_y = y

        if current_row:
            rows.append(sorted(current_row, key=lambda x: x["bbox"][0]))

        return [[cell["text"] for cell in row] for row in rows]