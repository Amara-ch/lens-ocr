"""Command-line interface for lens-ocr."""
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(help="lens-ocr - document understanding CLI")
console = Console()


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

    console.print(f"\n[bold green]Done![/bold green]")
    console.print(f"Output saved to: [cyan]{output}[/cyan]")
    console.print(f"\n[bold]Preview:[/bold]")
    console.print("-" * 60)
    console.print(markdown[:1500] + ("..." if len(markdown) > 1500 else ""))
    console.print("-" * 60)


def main():
    app()


if __name__ == "__main__":
    main()
