"""Main document understanding pipeline."""
import time
import uuid
from pathlib import Path

import numpy as np
from PIL import Image
from pdf2image import convert_from_path

from .schemas import DocumentResult, Region, BoundingBox, RegionType
from .ocr.text_extractor import TextExtractor
from .layout.detector import LayoutDetector
from .equations.latex_converter import LatexConverter
from .tables.extractor import TableExtractor


# Map layout labels to RegionType enum
LABEL_TO_REGION = {
    "title": RegionType.TITLE,
    "section-header": RegionType.TITLE,
    "text": RegionType.TEXT,
    "table": RegionType.TABLE,
    "figure": RegionType.FIGURE,
    "picture": RegionType.FIGURE,
    "equation": RegionType.EQUATION,
    "formula": RegionType.EQUATION,
    "list-item": RegionType.LIST,
    "page-header": RegionType.HEADER,
    "page-footer": RegionType.FOOTER,
    "caption": RegionType.TEXT,
}


class DocumentPipeline:
    """End-to-end document parsing pipeline."""

    def __init__(self, lang: str = "en", use_gpu: bool = False, enable_latex: bool = True):
        print("Loading models (first run downloads weights — be patient)...")
        self.text_extractor = TextExtractor(lang=lang, use_gpu=use_gpu)
        self.layout_detector = LayoutDetector()
        self.table_extractor = TableExtractor(self.text_extractor)
        self.enable_latex = enable_latex
        self.latex_converter = None
        if enable_latex:
            try:
                self.latex_converter = LatexConverter()
            except Exception as exc:
                print(f"Warning: LaTeX converter unavailable: {exc}")
                self.enable_latex = False
        print("Pipeline ready!")

    def _load_pages(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        if path.suffix.lower() == ".pdf":
            return convert_from_path(str(path), dpi=200)
        return [Image.open(path).convert("RGB")]

    @staticmethod
    def _bbox_to_schema(bbox):
        return BoundingBox(x_min=bbox[0], y_min=bbox[1], x_max=bbox[2], y_max=bbox[3])

    @staticmethod
    def _map_region_type(label):
        return LABEL_TO_REGION.get(label.lower(), RegionType.TEXT)

    @staticmethod
    def _table_to_markdown(rows):
        if not rows:
            return ""
        header = "| " + " | ".join(rows[0]) + " |"
        sep = "| " + " | ".join("---" for _ in rows[0]) + " |"
        body = "\n".join("| " + " | ".join(r) + " |" for r in rows[1:])
        return "\n".join([header, sep, body]) if rows[1:] else "\n".join([header, sep])

    def process(self, file_path):
        start = time.time()
        pages = self._load_pages(file_path)
        all_regions = []

        for page_num, page in enumerate(pages, start=1):
            layout_regions = self.layout_detector.detect(page)

            for layout in layout_regions:
                region_type = self._map_region_type(layout["type"])
                bbox = layout["bbox"]
                cropped = page.crop(bbox)

                region = Region(
                    id=str(uuid.uuid4())[:8],
                    type=region_type,
                    bbox=self._bbox_to_schema(bbox),
                    confidence=layout["confidence"],
                    page=page_num,
                )

                if region_type == RegionType.EQUATION:
                    if self.enable_latex and self.latex_converter is not None:
                        region.latex = self.latex_converter.convert(cropped)
                    else:
                        region.latex = "% LaTeX disabled (torch DLL conflict on Windows)"
                elif region_type == RegionType.TABLE:
                    region.table_data = self.table_extractor.extract(cropped)
                elif region_type in (RegionType.FIGURE, RegionType.CHART):
                    pass
                else:
                    cells = self.text_extractor.extract(np.array(cropped))
                    region.text = " ".join(c["text"] for c in cells).strip()

                all_regions.append(region)

        all_regions.sort(key=lambda r: (r.page, r.bbox.y_min))

        md_lines = []
        for r in all_regions:
            if r.type == RegionType.TITLE and r.text:
                md_lines.append(f"# {r.text}")
            elif r.type == RegionType.EQUATION and r.latex:
                md_lines.append(f"$$\n{r.latex}\n$$")
            elif r.type == RegionType.TABLE and r.table_data:
                md_lines.append(self._table_to_markdown(r.table_data))
            elif r.type == RegionType.LIST and r.text:
                md_lines.append(f"- {r.text}")
            elif r.type in (RegionType.FIGURE, RegionType.CHART):
                md_lines.append(f"![{r.type.value}](page-{r.page}-region-{r.id})")
            elif r.text:
                md_lines.append(r.text)

        elapsed_ms = int((time.time() - start) * 1000)
        return DocumentResult(
            filename=Path(file_path).name,
            num_pages=len(pages),
            regions=all_regions,
            markdown="\n\n".join(md_lines),
            plain_text="\n".join(r.text for r in all_regions if r.text),
            processing_time_ms=elapsed_ms,
        )
