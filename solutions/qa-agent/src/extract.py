"""PDF extraction — converts PDF documents to structured markdown.

Two extraction engines:
    - **pymupdf4llm** (default): LLM-optimised markdown output from PyMuPDF.
      Preserves tables as markdown tables, handles headers/footers,
      and produces clean structured output. No GPU needed, instant.
      Install: pip install pymupdf4llm
    - **pymupdf**: Basic text extraction. Fastest, simplest fallback.
      Install: pip install pymupdf

Usage:
    # Default (pymupdf4llm) — best no-GPU option
    python extract.py

    # Basic PyMuPDF fallback
    python extract.py --engine pymupdf

    # Programmatic
    from extract import extract_pdf
    extract_pdf(Path("report.pdf"))
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

Engine = Literal["pymupdf4llm", "pymupdf"]


def extract_pdf(
    pdf_path: Path,
    *,
    engine: Engine = "pymupdf4llm",
    output_dir: Path | None = None,
    pages_per_file: int | None = None,
) -> list[Path]:
    """Extract a PDF to markdown files with page annotations.

    Args:
        pdf_path: Path to the source PDF.
        engine: "pymupdf4llm" (default) or "pymupdf".
        output_dir: Where to write markdown files.
        pages_per_file: Pages per output file (None = auto-detect).

    Returns:
        List of paths to the generated markdown files.
    """
    if output_dir is None:
        output_dir = pdf_path.parent.parent / "markdown"
    output_dir.mkdir(parents=True, exist_ok=True)

    if engine == "pymupdf4llm":
        return _extract_with_pymupdf4llm(
            pdf_path, output_dir=output_dir,
            pages_per_file=pages_per_file,
        )
    elif engine == "pymupdf":
        return _extract_with_pymupdf(
            pdf_path, output_dir=output_dir,
            pages_per_file=pages_per_file,
        )
    else:
        raise ValueError(
            f"Unknown engine: {engine!r}. "
            "Use 'pymupdf4llm' or 'pymupdf'."
        )


def extract_all_pdfs(
    originals_dir: Path,
    *,
    engine: Engine = "pymupdf4llm",
    output_dir: Path | None = None,
    pages_per_file: int | None = None,
) -> list[Path]:
    """Extract all PDFs in a directory to markdown."""
    if output_dir is None:
        output_dir = originals_dir.parent / "markdown"

    all_files: list[Path] = []
    for pdf_path in sorted(originals_dir.glob("*.pdf")):
        print(f"Extracting: {pdf_path.name} (engine={engine})")
        files = extract_pdf(
            pdf_path, engine=engine,
            output_dir=output_dir,
            pages_per_file=pages_per_file,
        )
        print(f"  -> {len(files)} markdown files")
        all_files.extend(files)

    return all_files


# ---------------------------------------------------------------------------
# Engine: pymupdf4llm (default)
# ---------------------------------------------------------------------------

def _extract_with_pymupdf4llm(
    pdf_path: Path,
    *,
    output_dir: Path,
    pages_per_file: int | None = None,
) -> list[Path]:
    """Extract PDF using pymupdf4llm — LLM-optimised markdown.

    Produces clean markdown with:
    - Tables preserved as markdown tables
    - Headers detected and converted to # headings
    - Page breaks annotated
    - Images referenced (not embedded)
    """
    import pymupdf4llm

    # Extract full document as markdown with page chunks
    md_pages = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=True,
        write_images=False,
    )

    # md_pages is a list of dicts: {"metadata": {...}, "text": "..."}
    # each dict is one page
    pages = []
    for item in md_pages:
        meta = item.get("metadata", {})
        page_num = meta.get("page", len(pages) + 1)
        text = item.get("text", "").strip()
        if text:
            pages.append({
                "page_number": page_num,
                "text": text,
            })

    if not pages:
        return []

    # Group pages into sections
    if pages_per_file:
        sections = _group_by_count(pages, pages_per_file)
    else:
        sections = _group_by_headings(pages)

    # Write each section as a markdown file
    doc_name = pdf_path.stem
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
# Engine: pymupdf (basic fallback)
# ---------------------------------------------------------------------------

def _extract_with_pymupdf(
    pdf_path: Path,
    *,
    output_dir: Path,
    pages_per_file: int | None = None,
) -> list[Path]:
    """Extract PDF using PyMuPDF — basic text extraction."""
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

    if pages_per_file:
        sections = _group_by_count(pages, pages_per_file)
    else:
        sections = _group_by_headings(pages)

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
    first_lines = text[:300].strip().split("\n")
    for line in first_lines[:5]:
        line = line.strip()
        # Markdown headings (pymupdf4llm produces these)
        md_match = re.match(r"^#{1,2}\s+(.+)$", line)
        if md_match:
            return md_match.group(1).strip()
        # All-caps headings
        if line and line == line.upper() and 3 < len(line) < 80:
            return line.title()
        # Title-case headings
        if line and line == line.title() and 3 < len(line) < 80:
            return line
    return None


def _group_by_count(
    pages: list[dict], per_file: int,
) -> list[dict]:
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
        choices=["pymupdf4llm", "pymupdf"],
        default="pymupdf4llm",
        help="Extraction engine (default: pymupdf4llm)",
    )
    parser.add_argument(
        "--pages-per-file",
        type=int,
        default=None,
        help="Pages per output file (default: auto-detect sections)",
    )
    args = parser.parse_args()

    kb_dir = Path(__file__).parent.parent / "knowledge_base"
    originals = kb_dir / "originals"

    pdfs = list(originals.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {originals}")
        print("Place the PetSure governance policy PDF in:")
        print(f"  {originals}/")
        raise SystemExit(1)

    print(f"Engine: {args.engine}")
    print()

    files = extract_all_pdfs(
        originals,
        engine=args.engine,
        pages_per_file=args.pages_per_file,
    )
    print(
        f"\nDone. {len(files)} markdown files "
        f"written to {kb_dir / 'markdown'}"
    )
