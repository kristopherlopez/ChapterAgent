"""Batched PDF extraction — processes large PDFs in page-range batches.

Solves memory issues with Marker on large documents by processing
N pages at a time, then combining the output.

Usage:
    python extract_batched.py
    python extract_batched.py --batch-size 10
    python extract_batched.py --use-llm --llm-service openrouter
"""

from __future__ import annotations

import gc
import os
import re
from pathlib import Path


def extract_pdf_batched(
    pdf_path: Path,
    *,
    output_dir: Path,
    batch_size: int = 20,
    use_llm: bool = False,
    llm_service: str = "gemini",
) -> list[Path]:
    """Extract a PDF using Marker in page-range batches.

    Processes `batch_size` pages at a time to avoid memory errors
    on large documents. Each batch produces markdown that is
    accumulated and then split into section files.
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser
    except ImportError:
        print("marker-pdf not installed. Install: pip install marker-pdf")
        raise SystemExit(1)

    # Get total page count
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    print(f"  Total pages: {total_pages}")
    print(f"  Batch size: {batch_size}")
    print(f"  Batches: {(total_pages + batch_size - 1) // batch_size}")
    print()

    # Build base config
    config_dict: dict = {
        "output_format": "markdown",
        "highres_image_dpi": 96,
        "lowres_image_dpi": 72,
    }

    if use_llm:
        config_dict["use_llm"] = True
        if llm_service == "openrouter":
            config_dict["llm_service"] = "marker.services.openai"
            config_dict["openai_base_url"] = (
                "https://openrouter.ai/api/v1"
            )
            config_dict["openai_api_key"] = os.environ.get(
                "OPENROUTER_API_KEY", "",
            )
            config_dict["openai_model"] = os.environ.get(
                "OPENROUTER_MODEL",
                "google/gemini-2.5-flash-preview",
            )
        else:
            config_dict["llm_service"] = llm_service

    # Load models once (reuse across batches)
    print("Loading Marker models...")
    artifact_dict = create_model_dict()

    all_markdown_parts: list[str] = []

    for batch_start in range(0, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        page_range = list(range(batch_start, batch_end))

        batch_num = (batch_start // batch_size) + 1
        total_batches = (total_pages + batch_size - 1) // batch_size
        print(
            f"  Batch {batch_num}/{total_batches}: "
            f"pages {batch_start + 1}-{batch_end}..."
        )

        # Set page range for this batch (Marker expects "start-end" string)
        range_str = f"{batch_start}-{batch_end - 1}"
        batch_config = {**config_dict, "page_range": range_str}
        config_parser = ConfigParser(batch_config)

        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=artifact_dict,
        )

        rendered = converter(str(pdf_path))
        batch_md = rendered.markdown

        # Add page offset annotations
        batch_md = _inject_page_markers(
            batch_md, batch_start + 1,
        )

        all_markdown_parts.append(batch_md)

        # Free memory between batches
        del converter, rendered
        gc.collect()

    # Combine all batches
    full_markdown = "\n\n".join(all_markdown_parts)

    # Split into section files
    output_dir.mkdir(parents=True, exist_ok=True)
    sections = _split_into_sections(full_markdown, pdf_path.stem)

    written_files: list[Path] = []
    for i, section in enumerate(sections, 1):
        filename = f"{i:02d}-{section['slug']}.md"
        filepath = output_dir / filename
        filepath.write_text(section["content"], encoding="utf-8")
        written_files.append(filepath)

    return written_files


def _inject_page_markers(markdown: str, start_page: int) -> str:
    """Add a page marker comment at the start of each batch."""
    return f"<!-- Page {start_page} -->\n\n{markdown}"


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:50]


def _split_into_sections(
    markdown: str,
    doc_name: str,
) -> list[dict]:
    """Split combined markdown into section files by # headings."""
    parts = re.split(r"(?=^# [^#])", markdown, flags=re.MULTILINE)

    sections = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        heading_match = re.match(r"^# (.+)$", part, re.MULTILINE)
        title = heading_match.group(1).strip() if heading_match else "Section"

        # Deduplicate: skip if same title as previous
        if sections and sections[-1]["title"] == title:
            sections[-1]["content"] += "\n\n" + part
            continue

        sections.append({
            "title": title,
            "slug": _slugify(title),
            "content": part,
        })

    if not sections:
        sections.append({
            "title": doc_name,
            "slug": _slugify(doc_name),
            "content": markdown,
        })

    return sections


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract PDF in batches using Marker",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Pages per batch (default: 20)",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable LLM enhancement for better tables",
    )
    parser.add_argument(
        "--llm-service",
        default="gemini",
        choices=[
            "gemini", "anthropic", "openai",
            "ollama", "openrouter",
        ],
        help="LLM backend (default: gemini)",
    )
    args = parser.parse_args()

    kb_dir = Path(__file__).parent.parent / "knowledge_base"
    originals = kb_dir / "originals"
    markdown_dir = kb_dir / "markdown"

    pdfs = list(originals.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {originals}")
        raise SystemExit(1)

    # Clear existing markdown
    for old_md in markdown_dir.glob("*.md"):
        old_md.unlink()

    for pdf_path in pdfs:
        print(f"Extracting: {pdf_path.name}")
        files = extract_pdf_batched(
            pdf_path,
            output_dir=markdown_dir,
            batch_size=args.batch_size,
            use_llm=args.use_llm,
            llm_service=args.llm_service,
        )
        print(f"  -> {len(files)} markdown files")

    print(f"\nDone. Files written to {markdown_dir}")
    print("Run 'python ingest.py --skip-extract' to chunk and embed.")
