"""Context retrieval — hybrid search against ChromaDB."""

from __future__ import annotations

from pathlib import Path

import chromadb
from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A chunk retrieved from the document corpus."""
    text: str
    document: str
    page: int
    section: str
    score: float = Field(default=0.0, description="Similarity score (0-1, higher is better)")
    chunk_index: int = 0


class HybridRetriever:
    """Hybrid retrieval: vector similarity + keyword matching against ChromaDB.

    Usage:
        retriever = HybridRetriever.from_knowledge_base(kb_dir)
        chunks = retriever.retrieve("What was CBA's net interest margin?", top_k=5)
    """

    def __init__(self, collection: chromadb.Collection):
        self._collection = collection

    @classmethod
    def from_knowledge_base(
        cls,
        knowledge_base_dir: Path,
        *,
        collection_name: str = "cba_annual_report",
    ) -> HybridRetriever:
        """Create retriever from a knowledge base directory, ingesting if needed."""
        persist_dir = str(knowledge_base_dir / ".chromadb")

        # Fast path: reuse persisted collection if it exists and has data
        try:
            client = chromadb.PersistentClient(path=persist_dir)
            existing = client.get_collection(collection_name)
            if existing.count() > 0:
                print(f"Loaded persisted ChromaDB collection ({existing.count()} chunks)")
                return cls(existing)
        except Exception:
            pass

        # Slow path: full ingestion
        from ingest import ingest_knowledge_base

        collection = ingest_knowledge_base(
            knowledge_base_dir,
            collection_name=collection_name,
            persist_directory=persist_dir,
            skip_extract=True,
        )
        return cls(collection)

    @classmethod
    def from_collection(cls, collection: chromadb.Collection) -> HybridRetriever:
        """Create retriever from an existing ChromaDB collection."""
        return cls(collection)

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a query.

        Uses ChromaDB's built-in embedding + similarity search.
        Falls back gracefully if the collection is empty.
        """
        if self._collection.count() == 0:
            return []

        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            # ChromaDB returns distances (lower = more similar for cosine)
            # Convert to similarity score (higher = better)
            similarity = max(0.0, 1.0 - dist)
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    document=meta.get("document", "Unknown"),
                    page=meta.get("page", 0),
                    section=meta.get("section", "Unknown"),
                    score=round(similarity, 4),
                    chunk_index=meta.get("chunk_index", 0),
                )
            )

        return sorted(chunks, key=lambda c: c.score, reverse=True)
