"""Command-line interface for lens-ocr."""
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(help="lens-ocr - document understanding CLI")
console = Console()


def _generate_html(md_path: Path, html_path: Path):
    """Convert markdown to beautiful HTML with MathJax rendering."""
    markdown = md_path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in markdown.split("\n\n") if b.strip()]
    content_html = "\n".join(f'<div class="math-line">{b}</div>' for b in blocks)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>lens-ocr - {md_path.stem}</title>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 900px; margin: 40px auto; padding: 30px; line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
    h1 {{ color: white; margin-bottom: 10px; }}
    .badge {{ display: inline-block; padding: 6px 14px; background: #10b981; color: white; border-radius: 20px; font-size: 14px; font-weight: bold; margin-left: 10px; }}
    .subtitle {{ color: rgba(255,255,255,0.85); margin-bottom: 30px; }}
    #content {{ background: white; padding: 50px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }}
    .math-line {{ padding: 20px 0; border-bottom: 1px solid #f0f0f0; font-size: 18px; }}
    .math-line:last-child {{ border-bottom: none; }}
    .footer {{ text-align: center; margin-top: 30px; color: rgba(255,255,255,0.85); font-size: 14px; }}
    .footer a {{ color: #fef3c7; text-decoration: none; font-weight: bold; }}
    .stats {{ display: flex; gap: 20px; margin-top: 20px; }}
    .stat {{ background: rgba(255,255,255,0.15); padding: 15px 20px; border-radius: 12px; color: white; flex: 1; }}
    .stat .label {{ font-size: 12px; opacity: 0.8; }}
    .stat .value {{ font-size: 24px; font-weight: bold; margin-top: 4px; }}
  </style>
</head>
<body>
<h1>lens-ocr Smart Mode<span class="badge">MISTRAL-QUALITY</span></h1>
<div class="subtitle">{md_path.stem} — Extracted via Gemini Vision</div>
<div class="stats">
  <div class="stat"><div class="label">Engine</div><div class="value">Gemini 2.5 Flash</div></div>
  <div class="stat"><div class="label">Quality</div><div class="value">Excellent</div></div>
  <div class="stat"><div class="label">Cost</div><div class="value">FREE</div></div>
</div>
<br>
<div id="content">
{content_html}
</div>
<div class="footer">Built with <a href="https://github.com/Amara-ch/lens-ocr">lens-ocr</a> | Powered by Google Gemini</div>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")


@app.command()
def info():
    """Show information about lens-ocr."""
    console.print("[bold cyan]lens-ocr v0.1.0[/bold cyan]")
    console.print("[bold]Local mode (lens-ocr parse):[/bold]")
    console.print("  Layout detection: titles, tables, figures, equations, lists")
    console.print("  OCR: 80+ languages via PaddleOCR")
    console.print("  Equation -> LaTeX via pix2tex")
    console.print("  Table extraction with row grouping")
    console.print("")
    console.print("[bold green]Smart mode (lens-ocr smart):[/bold green]")
    console.print("  Gemini Vision -> Mistral-quality Markdown output")
    console.print("  Handles handwriting, complex equations, mixed layouts")
    console.print("  Auto-generates beautiful HTML preview")


@app.command()
def parse(
    file: Path = typer.Argument(..., help="Path to image or PDF"),
    output: Path = typer.Option("output.json", "-o", "--output", help="Output JSON path"),
    lang: str = typer.Option("en", "--lang", help="OCR language code"),
):
    """Parse a document using LOCAL OCR (PaddleOCR + PP-Structure)."""
    from .pipeline import DocumentPipeline

    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    with console.status("[bold yellow]Loading models..."):
        pipeline = DocumentPipeline(lang=lang)

    console.print(f"\n[bold]Parsing[/bold] [cyan]{file.name}[/cyan]...")
    result = pipeline.process(file)
    output.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    table = Table(title="\nParsing complete!")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("File", result.filename)
    table.add_row("Pages", str(result.num_pages))
    table.add_row("Regions detected", str(len(result.regions)))
    table.add_row("Processing time", f"{result.processing_time_ms} ms")
    table.add_row("Output saved to", str(output))
    console.print(table)


@app.command()
def smart(
    file: Path = typer.Argument(..., help="Path to image"),
    output: Path = typer.Option("smart-output.md", "-o", "--output", help="Output Markdown path"),
    html: bool = typer.Option(True, "--html/--no-html", help="Also generate HTML preview"),
    api_key: Optional[str] = typer.Option(None, "--key", help="Gemini API key (or use GEMINI_API_KEY env)"),
    model: str = typer.Option("gemini-2.5-flash", "--model", help="Gemini model name"),
):
    """Parse using Gemini Vision -- Mistral-quality output for handwriting & equations."""
    from .cloud.gemini_vision import GeminiVision

    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    try:
        vision = GeminiVision(api_key=api_key, model=model)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Sending[/bold] [cyan]{file.name}[/cyan] to [bold green]{model}[/bold green]...")
    with console.status("[bold yellow]Generating Markdown..."):
        markdown = vision.parse(file)

    output.write_text(markdown, encoding="utf-8")

    html_path = None
    if html:
        html_path = output.with_suffix(".html")
        _generate_html(output, html_path)

    console.print(f"\n[bold green]Done![/bold green]")
    console.print(f"Markdown: [cyan]{output}[/cyan]")
    if html_path:
        console.print(f"HTML preview: [cyan]{html_path}[/cyan]  [dim](open in browser to see rendered math)[/dim]")
    console.print(f"\n[bold]Preview:[/bold]")
    console.print("-" * 60)
    console.print(markdown[:1500] + ("..." if len(markdown) > 1500 else ""))
    console.print("-" * 60)


def main():
    app()


if __name__ == "__main__":
    main()
