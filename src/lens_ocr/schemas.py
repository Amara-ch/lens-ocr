"""Pydantic schemas defining the structured output of lens-ocr."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RegionType(str, Enum):
    """Types of regions we can detect in a document."""
    TEXT = "text"
    TITLE = "title"
    TABLE = "table"
    FIGURE = "figure"
    EQUATION = "equation"
    SIGNATURE = "signature"
    CHART = "chart"
    LIST = "list"
    HEADER = "header"
    FOOTER = "footer"


class BoundingBox(BaseModel):
    """Axis-aligned bounding box in pixel coordinates."""
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        return self.y_max - self.y_min


class Region(BaseModel):
    """A single detected region within a document page."""
    id: str
    type: RegionType
    bbox: BoundingBox
    confidence: float = Field(..., ge=0.0, le=1.0)
    page: int = 1

    # Content fields (only some are set, depending on region type)
    text: Optional[str] = None
    latex: Optional[str] = None
    table_data: Optional[List[List[str]]] = None


class DocumentResult(BaseModel):
    """Complete parsed output of a document."""
    filename: str
    num_pages: int
    regions: List[Region]
    markdown: str = ""
    plain_text: str = ""
    processing_time_ms: int = 0
