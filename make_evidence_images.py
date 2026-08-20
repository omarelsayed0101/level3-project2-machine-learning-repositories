"""Render reproducible terminal-style evidence images from captured project logs."""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = PROJECT_DIR / "evidence"

try:
    font = ImageFont.truetype("DejaVuSansMono.ttf", 20)
    small_font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
except OSError:
    font = ImageFont.load_default()
    small_font = font


def render(source: str, output: str, title: str) -> None:
    raw = (EVIDENCE_DIR / source).read_text(encoding="utf-8", errors="replace")
    lines: list[str] = []
    for paragraph in raw.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=112) or [""])
    lines = lines[:44]
    line_height = 27
    image = Image.new("RGB", (2400, 150 + line_height * max(1, len(lines))), "#0d1117")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 92), fill="#161b22")
    draw.text((42, 28), title, fill="#58a6ff", font=font)
    y = 118
    for line in lines:
        draw.text((42, y), line, fill="#c9d1d9", font=small_font)
        y += line_height
    image.save(EVIDENCE_DIR / output)


render("init_status.txt", "init_status.png", "Git evidence — initialize and inspect status")
render("staging_status.txt", "staging_status.png", "Git evidence — stage project files")
render("commit_output.txt", "commit_output.png", "Git evidence — first commit and clean status")
render("repository_inspection.json", "github_connection.png", "GitHub evidence — repository connection")
render("github_publication_verified.md", "github_publication.png", "GitHub evidence — publication verified")
print("Rendered evidence images.")
