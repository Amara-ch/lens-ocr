"""Basic tests for lens-ocr schemas (no model downloads required)."""
import pytest
from lens_ocr.schemas import (
    BoundingBox,
    DocumentResult,
    Region,
    RegionType,
)


def test_bounding_box_dimensions():
    bbox = BoundingBox(x_min=10, y_min=20, x_max=110, y_max=220)
    assert bbox.width == 100
    assert bbox.height == 200


def test_region_creation():
    region = Region(
        id="abc12345",
        type=RegionType.TITLE,
        bbox=BoundingBox(x_min=0, y_min=0, x_max=100, y_max=50),
        confidence=0.97,
        text="Hello World",
    )
    assert region.type == RegionType.TITLE
    assert region.confidence == 0.97
    assert region.text == "Hello World"
    assert region.latex is None


def test_region_invalid_confidence():
    with pytest.raises(ValueError):
        Region(
            id="x",
            type=RegionType.TEXT,
            bbox=BoundingBox(x_min=0, y_min=0, x_max=1, y_max=1),
            confidence=1.5,  # invalid: must be <= 1.0
        )


def test_document_result_defaults():
    doc = DocumentResult(filename="test.pdf", num_pages=1, regions=[])
    assert doc.markdown == ""
    assert doc.plain_text == ""
    assert doc.processing_time_ms == 0


def test_equation_region_carries_latex():
    region = Region(
        id="eq1",
        type=RegionType.EQUATION,
        bbox=BoundingBox(x_min=0, y_min=0, x_max=200, y_max=80),
        confidence=0.92,
        latex=r"\int_0^1 x^2 \, dx",
    )
    assert region.latex == r"\int_0^1 x^2 \, dx"
    assert region.text is None