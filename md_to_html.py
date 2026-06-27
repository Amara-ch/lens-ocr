"""Convert lens-ocr Markdown output to beautiful HTML with rendered math."""
import sys
from pathlib import Path

def md_to_html(md_path: str, html_path: str = None):
    md_path = Path(md_path)
    if html_path is None:
        html_path = md_path.with_suffix(".html")
    else:
        html_path = Path(html_path)

    markdown = md_path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in markdown.split("\n\n") if b.strip()]
    content_html = "\n".join(f'<div class="math-line">{b}</div>' for b in blocks)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>lens-ocr Result - {md_path.stem}</title>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 900px; margin: 40px auto; padding: 30px; line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
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
<div class="footer">Built by <a href="https://github.com/Amara-ch/lens-ocr">@Amara-ch</a> with lens-ocr | Powered by Google Gemini</div>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    print(f"Created: {html_path}")
    return html_path

if __name__ == "__main__":
    md = sys.argv[1] if len(sys.argv) > 1 else "quadratic.md"
    out = sys.argv[2] if len(sys.argv) > 2 else None
    md_to_html(md, out)
