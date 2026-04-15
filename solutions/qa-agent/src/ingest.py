"""Document ingestion — full pipeline from PDF to ChromaDB.

Pipeline:
    1. Extract: PDF (originals/) -> markdown (markdown/)
       Engine: pymupdf4llm (default) or pymupdf (basic fallback)
    2. Chunk:   markdown -> structured chunks with metadata
    3. Embed:   chunks -> ChromaDB collection via embedding model
    4. Save:    chunks written to chunks/ as JSON for inspection

Usage:
    # Full pipeline (default: pymupdf4llm)
    python ingest.py

    # Full pipeline with basic PyMuPDF
    python ingest.py --engine pymupdf

    # Just re-chunk and re-embed existing markdown
    python ingest.py --skip-extract

    # Programmatic
    from ingest import ingest_knowledge_base
    collection = ingest_knowledge_base(Path("../knowledge_base"))
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from typing import Literal

import chromadb

Engine = Literal["pymupdf4llm", "pymupdf"]


# ---------------------------------------------------------------------------
# Step 1: Extract (PDF -> Markdown)
# ---------------------------------------------------------------------------

def extract_pdfs(
    knowledge_base_dir: Path,
    *,
    engine: Engine = "pymupdf4llm",
) -> list[Path]:
    """Extract all PDFs in originals/ to markdown/.

    Skips extraction if no PDFs are present (uses existing markdown).
    """
    originals_dir = knowledge_base_dir / "originals"
    markdown_dir = knowledge_base_dir / "markdown"

    pdfs = list(originals_dir.glob("*.pdf")) if originals_dir.exists() else []
    if not pdfs:
        return list(sorted(markdown_dir.glob("*.md")))

    try:
        from extract import extract_all_pdfs
    except ImportError:
        print("Warning: extract module unavailable, skipping PDF extraction")
        return list(sorted(markdown_dir.glob("*.md")))

    # Clear existing markdown before re-extracting
    for old_md in markdown_dir.glob("*.md"):
        old_md.unlink()

    try:
        extract_all_pdfs(
            originals_dir,
            engine=engine,
            output_dir=markdown_dir,
        )
    except Exception as e:
        print(f"Warning: PDF extraction failed ({e}), using existing markdown")

    return list(sorted(markdown_dir.glob("*.md")))


# ---------------------------------------------------------------------------
# Step 2: Chunk (Markdown -> structured chunks)
# ---------------------------------------------------------------------------

def chunk_markdown(
    text: str,
    *,
    document_name: str,
    source_file: str = "",
    max_chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """Split markdown text into chunks with metadata.

    Splits on section headers first, then by word count.
    Each chunk carries metadata for citation:
        - document: source document name
        - page: page number (from <!-- Page N --> comments)
        - section: section heading
        - source_file: originating markdown file
        - chunk_index: position in the chunk sequence
    """
    chunks = []
    current_page = 1
    current_section = "Introduction"

    # Split by headers
    sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        # Extract page from comments like <!-- Page 12 -->
        page_matches = re.findall(
            r"<!--\s*Page\s+(\d+)\s*-->", section,
        )
        if page_matches:
            current_page = int(page_matches[0])

        # Extract section title
        title_match = re.match(
            r"^(#{1,3})\s+(.+)$", section, re.MULTILINE,
        )
        if title_match:
            current_section = title_match.group(2).strip()

        # Clean section text (remove HTML comments, source lines)
        clean_text = re.sub(r"<!--.*?-->", "", section).strip()
        clean_text = re.sub(
            r"^\*Source:.*\*$", "", clean_text, flags=re.MULTILINE,
        ).strip()
        if not clean_text:
            continue

        # Split long sections into sub-chunks by word count
        words = clean_text.split()
        step = max(max_chunk_size - overlap, 1)
        for i in range(0, len(words), step):
            chunk_words = words[i : i + max_chunk_size]
            if len(chunk_words) < 20:
                continue

            # Track page number for multi-page sections
            page_for_chunk = current_page
            if page_matches and len(page_matches) > 1:
                # Estimate which page this chunk falls on
                progress = i / max(len(words), 1)
                page_idx = min(
                    int(progress * len(page_matches)),
                    len(page_matches) - 1,
                )
                page_for_chunk = int(page_matches[page_idx])

            chunk_text = " ".join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "document": document_name,
                    "page": page_for_chunk,
                    "section": current_section,
                    "source_file": source_file,
                    "chunk_index": len(chunks),
                },
            })

    return chunks


def chunk_all_markdown(
    markdown_dir: Path,
    *,
    document_name: str = "PetSure Governance Policies",
    max_chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """Chunk all markdown files in a directory."""
    all_chunks = []
    for md_file in sorted(markdown_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_markdown(
            text,
            document_name=document_name,
            source_file=md_file.name,
            max_chunk_size=max_chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(chunks)
    return all_chunks


# ---------------------------------------------------------------------------
# Step 3: Save chunks to disk (for inspection / debugging)
# ---------------------------------------------------------------------------

def save_chunks(
    chunks: list[dict],
    output_dir: Path,
) -> Path:
    """Save chunks to JSON for inspection.

    Writes two files:
        - chunks.json: full chunk data with metadata
        - chunks_summary.json: stats and sample
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = output_dir / "chunks.json"
    summary_path = output_dir / "chunks_summary.json"

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    # Build summary
    sections = set()
    pages = set()
    for c in chunks:
        sections.add(c["metadata"]["section"])
        pages.add(c["metadata"]["page"])

    summary = {
        "total_chunks": len(chunks),
        "unique_sections": len(sections),
        "page_range": [min(pages), max(pages)] if pages else [],
        "avg_chunk_length_words": (
            sum(len(c["text"].split()) for c in chunks) // max(len(chunks), 1)
        ),
        "sections": sorted(sections),
        "sample_chunk": chunks[0] if chunks else None,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return chunks_path


# ---------------------------------------------------------------------------
# Step 4: Embed and store in ChromaDB
# ---------------------------------------------------------------------------

def embed_chunks(
    chunks: list[dict],
    *,
    collection_name: str = "petsure_governance_policies",
    persist_directory: str | None = None,
) -> chromadb.Collection:
    """Embed chunks and store in ChromaDB.

    Uses ChromaDB's default embedding function (all-MiniLM-L6-v2).
    For production, swap to OpenAI text-embedding-3-small via:
        chromadb.utils.embedding_functions.OpenAIEmbeddingFunction
    """
    if persist_directory:
        client = chromadb.PersistentClient(path=persist_directory)
    else:
        client = chromadb.Client()

    # Check if collection already exists with the right count
    try:
        existing = client.get_collection(collection_name)
        if existing.count() == len(chunks) and len(chunks) > 0:
            print(f"Reusing existing ChromaDB collection ({existing.count()} chunks)")
            return existing
    except Exception:
        pass

    # Clean slate — re-embed
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    if not chunks:
        return collection

    # Batch add to avoid memory issues with large chunk sets
    batch_size = 200
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[f"chunk_{j:04d}" for j in range(i, i + len(batch))],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )

    return collection


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def ingest_knowledge_base(
    knowledge_base_dir: Path,
    *,
    collection_name: str = "petsure_governance_policies",
    persist_directory: str | None = None,
    document_name: str = "PetSure Governance Policies",
    skip_extract: bool = False,
    engine: Engine = "pymupdf4llm",
) -> chromadb.Collection:
    """Full ingestion pipeline: extract -> chunk -> save -> embed.

    Args:
        knowledge_base_dir: Root knowledge base directory containing
            originals/, markdown/, and chunks/ subdirectories.
        collection_name: ChromaDB collection name.
        persist_directory: If set, persist ChromaDB to this path.
        document_name: Human-readable document name for citations.
        skip_extract: If True, skip PDF extraction (use existing markdown).
        engine: PDF extraction engine — "pymupdf4llm" (default) or "pymupdf".

    Returns:
        ChromaDB collection with embedded chunks.
    """
    markdown_dir = knowledge_base_dir / "markdown"
    chunks_dir = knowledge_base_dir / "chunks"

    # Step 1: Extract PDFs (if present and not skipped)
    if not skip_extract:
        extract_pdfs(knowledge_base_dir, engine=engine)

    # Step 2: Chunk markdown (or reuse existing chunks if markdown is empty)
    md_files = list(markdown_dir.glob("*.md"))
    if md_files:
        chunks = chunk_all_markdown(
            markdown_dir, document_name=document_name,
        )
        print(f"Chunked {len(chunks)} chunks from {markdown_dir}")
    else:
        # No markdown available — try loading pre-existing chunks
        existing_chunks_path = chunks_dir / "chunks.json"
        if existing_chunks_path.exists():
            with open(existing_chunks_path, encoding="utf-8") as f:
                chunks = json.load(f)
            print(f"Loaded {len(chunks)} pre-existing chunks from {existing_chunks_path}")
        else:
            chunks = []
            print("No markdown files and no existing chunks found")

    # Step 3: Save chunks to disk
    chunks_path = save_chunks(chunks, chunks_dir)
    print(f"Saved chunks to {chunks_path}")

    # Step 4: Embed and store
    collection = embed_chunks(
        chunks,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    print(f"Embedded {collection.count()} chunks in ChromaDB")

    return collection


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest knowledge base: PDF -> markdown -> chunks -> ChromaDB",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip PDF extraction, use existing markdown",
    )
    parser.add_argument(
        "--engine",
        choices=["pymupdf4llm", "pymupdf"],
        default="pymupdf4llm",
        help="PDF extraction engine (default: pymupdf4llm)",
    )
    args = parser.parse_args()

    kb_dir = Path(__file__).parent.parent / "knowledge_base"

    print(f"Knowledge base: {kb_dir}")
    print(f"  originals/  -> PDF source documents")
    print(f"  markdown/   -> extracted markdown")
    print(f"  chunks/     -> chunked content (JSON)")
    if not args.skip_extract:
        print(f"  engine:     {args.engine}")
    print()

    originals = kb_dir / "originals"
    pdfs = (
        list(originals.glob("*.pdf")) if originals.exists() else []
    )
    md_files = list((kb_dir / "markdown").glob("*.md"))

    if not pdfs and not md_files:
        print("No PDFs in originals/ and no markdown files.")
        print(f"Place the PetSure governance policy PDF in: {originals}/")
        raise SystemExit(1)

    if pdfs:
        names = ", ".join(p.name for p in pdfs)
        print(f"Found {len(pdfs)} PDF(s): {names}")
    if args.skip_extract:
        print("Skipping PDF extraction (--skip-extract)")
    print()

    collection = ingest_knowledge_base(
        kb_dir,
        skip_extract=args.skip_extract,
        engine=args.engine,
    )
    print(f"\nDone. {collection.count()} chunks ready for retrieval.")
