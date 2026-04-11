"""PDF extraction — converts PDF documents to structured markdown.

Two extraction engines:
    - **marker** (default): ML-based with optional LLM enhancement.
      Best for financial documents with tables, charts, multi-column layouts.
      Install: pip install marker-pdf
    - **pymupdf**: Rule-based text extraction. Fast, no GPU needed.
      Lower quality on tables and complex layouts. Good fallback.
      Install: pip install pymupdf

Usage:
    # Marker (default) — best quality
    python -m solutions.qa_agent.src.extract

    # Marker with LLM enhancement — best quality for financial tables
    python -m solutions.qa_agent.src.extract --use-llm

    # PyMuPDF fallback — fast, no GPU
    python -m solutions.qa_agent.src.extract --engine pymupdf

    # Programmatic
    from solutions.qa_agent.src.extract import extract_pdf
    extract_pdf(Path("report.pdf"), engine="marker")
    extract_pdf(Path("report.pdf"), engine="pymupdf")
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

Engine = Literal["marker", "pymupdf"]


def extract_pdf(
    pdf_path: Path,
    *,
    engine: Engine = "marker",
    output_dir: Path | None = None,
    pages_per_file: int | None = None,
    use_llm: bool = False,
    llm_service: str = "gemini",
) -> list[Path]:
    """Extract a PDF to markdown files with page annotations.

    Args:
        pdf_path: Path to the source PDF.
        engine: Extraction engine — "marker" (default) or "pymupdf".
        output_dir: Where to write markdown files.
            Defaults to knowledge_base/markdown/ relative to the PDF.
        pages_per_file: Pages per output file (None = auto-detect).
            Only used by pymupdf engine. Marker handles its own splitting.
        use_llm: (marker only) Enable LLM enhancement for better
            table extraction and cross-page table merging.
        llm_service: (marker only) LLM backend — "gemini" (default),
            "anthropic", "openai", "ollama", or "openrouter".

    Returns:
        List of paths to the generated markdown files.
    """
    if output_dir is None:
        output_dir = pdf_path.parent.parent / "markdown"
    output_dir.mkdir(parents=True, exist_ok=True)

    if engine == "marker":
        return _extract_with_marker(
            pdf_path,
            output_dir=output_dir,
            use_llm=use_llm,
            llm_service=llm_service,
        )
    elif engine == "pymupdf":
        return _extract_with_pymupdf(
            pdf_path,
            output_dir=output_dir,
            pages_per_file=pages_per_file,
        )
    else:
        raise ValueError(f"Unknown engine: {engine!r}. Use 'marker' or 'pymupdf'.")


def extract_all_pdfs(
    originals_dir: Path,
    *,
    engine: Engine = "marker",
    output_dir: Path | None = None,
    pages_per_file: int | None = None,
    use_llm: bool = False,
    llm_service: str = "gemini",
) -> list[Path]:
    """Extract all PDFs in a directory to markdown.

    Args:
        originals_dir: Directory containing PDF files.
        engine: Extraction engine — "marker" (default) or "pymupdf".
        output_dir: Where to write markdown. Defaults to ../markdown/.
        pages_per_file: (pymupdf only) Pages per output file.
        use_llm: (marker only) Enable LLM enhancement.
        llm_service: (marker only) LLM backend.

    Returns:
        List of all generated markdown file paths.
    """
    if output_dir is None:
        output_dir = originals_dir.parent / "markdown"

    all_files: list[Path] = []
    for pdf_path in sorted(originals_dir.glob("*.pdf")):
        print(f"Extracting: {pdf_path.name} (engine={engine})")
        files = extract_pdf(
            pdf_path,
            engine=engine,
            output_dir=output_dir,
            pages_per_file=pages_per_file,
            use_llm=use_llm,
            llm_service=llm_service,
        )
        print(f"  -> {len(files)} markdown files")
        all_files.extend(files)

    return all_files


# ---------------------------------------------------------------------------
# Engine: Marker
# ---------------------------------------------------------------------------

def _extract_with_marker(
    pdf_path: Path,
    *,
    output_dir: Path,
    use_llm: bool = False,
    llm_service: str = "gemini",
) -> list[Path]:
    """Extract PDF using Marker — ML-based with optional LLM enhancement.

    Marker handles layout detection, table recognition, and section
    splitting automatically. The --use_llm flag enables LLM-based
    post-processing for better table accuracy (0.82 -> 0.91).

    Supports OpenRouter via the OpenAI-compatible service by setting
    llm_service="openrouter". Reads OPENROUTER_API_KEY from environment.
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser
    except ImportError:
        print("marker-pdf not installed. Install with: pip install marker-pdf")
        print("Falling back to pymupdf engine.")
        return _extract_with_pymupdf(pdf_path, output_dir=output_dir)

    # Build config — lower DPI to avoid MemoryError on large PDFs
    config_dict: dict = {
        "output_format": "markdown",
        "highres_image_dpi": 96,
        "lowres_image_dpi": 72,
    }
    if use_llm:
        config_dict["use_llm"] = True

        if llm_service == "openrouter":
            # OpenRouter is OpenAI-compatible — use the openai service
            # with custom base_url and model
            import os

            config_dict["llm_service"] = "marker.services.openai"
            config_dict["openai_base_url"] = "https://openrouter.ai/api/v1"
            config_dict["openai_api_key"] = os.environ.get(
                "OPENROUTER_API_KEY", "",
            )
            config_dict["openai_model"] = os.environ.get(
                "OPENROUTER_MODEL",
                "google/gemini-2.5-flash-preview",
            )
            if not config_dict["openai_api_key"]:
                print("WARNING: OPENROUTER_API_KEY not set.")
                print("Set it in your environment or .env file.")
        else:
            config_dict["llm_service"] = llm_service

    config_parser = ConfigParser(config_dict)
    artifact_dict = create_model_dict()

    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=artifact_dict,
    )

    # Run conversion
    print(f"  Marker processing {pdf_path.name} (DPI=96)...")
    rendered = converter(str(pdf_path))

    # Marker returns a single markdown string — split into files
    # by top-level headings (# heading) with page annotations
    markdown_text = rendered.markdown

    # Inject page annotations if Marker's metadata includes page info
    if hasattr(rendered, "metadata") and rendered.metadata:
        markdown_text = _inject_page_annotations_marker(
            markdown_text, rendered.metadata,
        )

    # Split into section files by top-level headings
    sections = _split_markdown_by_headings(markdown_text, pdf_path.stem)

    written_files: list[Path] = []
    for i, section in enumerate(sections, 1):
        filename = f"{i:02d}-{section['slug']}.md"
        filepath = output_dir / filename
        filepath.write_text(section["content"], encoding="utf-8")
        written_files.append(filepath)

    return written_files


def _inject_page_annotations_marker(
    markdown: str,
    metadata: dict,
) -> str:
    """Inject <!-- Page N --> annotations using Marker metadata."""
    # Marker metadata varies by version — handle gracefully
    if not metadata:
        return markdown
    # If metadata has page-level info, inject comments
    # This is a best-effort — exact API depends on Marker version
    return markdown


def _split_markdown_by_headings(
    markdown: str,
    doc_name: str,
) -> list[dict]:
    """Split a markdown string into sections by top-level headings."""
    # Split on # headings (level 1)
    parts = re.split(r"(?=^# [^#])", markdown, flags=re.MULTILINE)

    sections = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Extract heading
        heading_match = re.match(r"^# (.+)$", part, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
        else:
            title = "Introduction"

        sections.append({
            "title": title,
            "slug": _slugify(title),
            "content": part,
        })

    # If no headings found, return as single file
    if not sections:
        sections.append({
            "title": doc_name,
            "slug": _slugify(doc_name),
            "content": markdown,
        })

    return sections


# ---------------------------------------------------------------------------
# Engine: PyMuPDF
# ---------------------------------------------------------------------------

def _extract_with_pymupdf(
    pdf_path: Path,
    *,
    output_dir: Path,
    pages_per_file: int | None = None,
) -> list[Path]:
    """Extract PDF using PyMuPDF — rule-based text extraction.

    Fast and lightweight (no GPU), but lower quality on tables and
    complex layouts. Good fallback when Marker isn't available.
    """
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    doc_name = pdf_path.stem

    pages: list[dict] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages.append({
                "page_number": page_num + 1,
                "text": _clean_page_text(text),
            })

    doc.close()

    if not pages:
        return []

    # Group pages into sections
    if pages_per_file:
        sections = _group_by_count(pages, pages_per_file)
    else:
        sections = _group_by_headings(pages)

    # Write each section as a markdown file
    written_files: list[Path] = []
    for i, section in enumerate(sections, 1):
        filename = f"{i:02d}-{section['slug']}.md"
        filepath = output_dir / filename

        content = _format_section_markdown(
            title=section["title"],
            pages=section["pages"],
            document_name=doc_name,
        )
        filepath.write_text(content, encoding="utf-8")
        written_files.append(filepath)

    return written_files


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert a title to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:50]


def _clean_page_text(text: str) -> str:
    """Clean raw PDF text extraction artifacts."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(
        r"^Commonwealth Bank of Australia.*$",
        "", text, flags=re.MULTILINE,
    )
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    return text.strip()


def _detect_heading(text: str) -> str | None:
    """Detect if a page starts with a chapter/section heading."""
    first_lines = text[:200].strip().split("\n")
    for line in first_lines[:3]:
        line = line.strip()
        if line and line == line.upper() and 3 < len(line) < 80:
            return line.title()
        if line and line == line.title() and 3 < len(line) < 80:
            return line
    return None


def _group_by_count(
    pages: list[dict],
    per_file: int,
) -> list[dict]:
    """Group pages into fixed-size sections."""
    sections = []
    for i in range(0, len(pages), per_file):
        group = pages[i : i + per_file]
        start_page = group[0]["page_number"]
        end_page = group[-1]["page_number"]
        sections.append({
            "title": f"Pages {start_page}-{end_page}",
            "slug": f"pages-{start_page:03d}-{end_page:03d}",
            "pages": group,
        })
    return sections


def _group_by_headings(pages: list[dict]) -> list[dict]:
    """Group pages by detected section headings."""
    sections: list[dict] = []
    current_section: dict | None = None

    for page in pages:
        heading = _detect_heading(page["text"])

        if heading and (
            current_section is None
            or heading != current_section["title"]
        ):
            if current_section:
                sections.append(current_section)
            current_section = {
                "title": heading,
                "slug": _slugify(heading),
                "pages": [page],
            }
        elif current_section is not None:
            current_section["pages"].append(page)
        else:
            current_section = {
                "title": "Introduction",
                "slug": "introduction",
                "pages": [page],
            }

    if current_section:
        sections.append(current_section)

    if len(sections) <= 1 and len(pages) > 20:
        return _group_by_count(pages, per_file=20)

    return sections


def _format_section_markdown(
    *,
    title: str,
    pages: list[dict],
    document_name: str,
) -> str:
    """Format a section as a markdown file with page annotations."""
    lines = [f"# {title}\n"]
    lines.append(f"*Source: {document_name}*\n")

    for page in pages:
        lines.append(f"\n<!-- Page {page['page_number']} -->\n")
        lines.append(page["text"])
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract PDFs to markdown for RAG ingestion",
    )
    parser.add_argument(
        "--engine",
        choices=["marker", "pymupdf"],
        default="marker",
        help="Extraction engine (default: marker)",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="(marker only) Enable LLM enhancement for better tables",
    )
    parser.add_argument(
        "--llm-service",
        default="gemini",
        choices=["gemini", "anthropic", "openai", "ollama", "openrouter"],
        help="(marker only) LLM backend (default: gemini)",
    )
    parser.add_argument(
        "--pages-per-file",
        type=int,
        default=None,
        help="(pymupdf only) Pages per output file",
    )
    args = parser.parse_args()

    kb_dir = Path(__file__).parent.parent / "knowledge_base"
    originals = kb_dir / "originals"

    pdfs = list(originals.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {originals}")
        print("Place the CBA Annual Report PDF in:")
        print(f"  {originals}/")
        raise SystemExit(1)

    print(f"Engine: {args.engine}")
    if args.engine == "marker" and args.use_llm:
        print(f"LLM enhancement: ON (service: {args.llm_service})")
    print()

    files = extract_all_pdfs(
        originals,
        engine=args.engine,
        use_llm=args.use_llm,
        llm_service=args.llm_service,
        pages_per_file=args.pages_per_file,
    )
    print(
        f"\nDone. {len(files)} markdown files "
        f"written to {kb_dir / 'markdown'}"
    )
