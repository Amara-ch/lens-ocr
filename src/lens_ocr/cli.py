"""Command-line interface for lens-ocr."""
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .pipeline import DocumentPipeline

app = typer.Typer(
    help="🔎 lens-ocr — open-source document understanding pipeline",
    no_args_is_help=True,
)
console = Console()


@app.command()
def parse(
    file: Path = typer.Argument(..., exists=True, help="PDF or image file"),
    output: Path = typer.Option("output.json", "-o", "--output", help="Output file path"),
    format: str = typer.Option("json", "-f", "--format", help="json | markdown | text"),
    lang: str = typer.Option("en", "-l", "--lang", help="OCR language code"),
    gpu: bool = typer.Option(False, "--gpu", help="Use GPU (requires CUDA)"),
):
    """Parse a document and extract structured content."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Loading models...", total=None)
        pipeline = DocumentPipeline(lang=lang, use_gpu=gpu)

    console.print(f"\n📄 Parsing [cyan]{file.name}[/cyan]...")
    result = pipeline.process(file)

    # Save output in requested format
    if format == "json":
        output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    elif format == "markdown":
        output.write_text(result.markdown, encoding="utf-8")
    elif format == "text":
        output.write_text(result.plain_text, encoding="utf-8")
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)

    # Pretty summary table
    table = Table(title="✨ Parsing complete!")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("File", result.filename)
    table.add_row("Pages", str(result.num_pages))
    table.add_row("Regions detected", str(len(result.regions)))
    table.add_row("Processing time", f"{result.processing_time_ms} ms")
    table.add_row("Output saved to", str(output))
    console.print(table)


@app.command()
def info():
    """Show lens-ocr version and capabilities."""
    console.print("[bold cyan]lens-ocr[/bold cyan] v0.1.0")
    console.print("📐 Layout detection: titles, tables, figures, equations, lists")
    console.print("🔤 OCR: 80+ languages via PaddleOCR")
    console.print("➗ Equation → LaTeX via pix2tex")
    console.print("📊 Table extraction with row grouping")


if __name__ == "__main__":
    app()