"""Cloud OCR via Google Gemini Vision."""
import os
from pathlib import Path
from typing import Optional, Union

import google.generativeai as genai
from PIL import Image


PROMPT = """You are an expert document parser. Extract ALL content from this image
and output as clean, well-structured Markdown.

Rules:
- Use LaTeX for ALL mathematical expressions:
  * Inline math: $...$
  * Display math: $$...$$
- Use proper LaTeX commands: \\frac{a}{b}, \\sqrt{x}, x_{i}, x^{2}, \\pm, \\cdot, \\times, \\div, \\leq, \\geq, \\neq, \\infty, \\sum, \\int, \\lim
- Preserve document structure: # for titles, ## for sections
- For tables, use Markdown table syntax with | separators
- For lists, use - bullets
- For equations on separate lines, use $$ display math
- Be PRECISE — every character matters in math
- For handwritten content, transcribe carefully
- Output ONLY the Markdown — no preamble, no "Here is the content..." just pure markdown
"""


class GeminiVision:
    """Google Gemini Vision API wrapper for high-quality document OCR."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set.\n"
                "Get a FREE key: https://aistudio.google.com/apikey\n"
                "Then set it: $env:GEMINI_API_KEY = 'your-key-here'"
            )
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def parse(self, image_path: Union[str, Path], prompt: Optional[str] = None) -> str:
        """Parse an image and return clean Markdown content."""
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = Image.open(image_path)
        response = self.model.generate_content([prompt or PROMPT, image])
        return response.text
