"""
backend/rag.py

RAG (Retrieval-Augmented Generation) pipeline for NoFishyBusiness.

Provides a single public function:

    retrieve(query, top_k=3) -> list[KBRecord]

which runs an FTS5 full-text search against the local SQLite knowledge base
and returns up to *top_k* matching records.

Requirements: 12.1, 12.2, 12.3, 12.7
"""

import os
import sqlite3

from backend.models import KBRecord

# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class RAGError(Exception):
    """Raised when the RAG pipeline encounters a database error.

    Callers should treat this as a 503-level failure: the knowledge base is
    unavailable and no LLM call should be made.
    """


# ---------------------------------------------------------------------------
# DB path helper
# ---------------------------------------------------------------------------

def _db_path() -> str:
    """Return the absolute path to knowledge_base/aquarium.db.

    Resolved relative to the project root (one level above backend/) so the
    path is correct regardless of the working directory used to launch the
    server.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "knowledge_base", "aquarium.db")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def retrieve(query: str, top_k: int = 3) -> list[KBRecord]:
    """Run FTS5 full-text search against the knowledge base.

    Executes::

        SELECT rowid, species_name, category, content
        FROM kb_fts
        WHERE kb_fts MATCH ?
        ORDER BY rank
        LIMIT ?

    Args:
        query:  The search string forwarded to the FTS5 MATCH operator.
        top_k:  Maximum number of records to return (default 3).

    Returns:
        A list of up to *top_k* :class:`~backend.models.KBRecord` objects.
        Returns an empty list when no records match the query.

    Raises:
        RAGError: On any :class:`sqlite3.Error`, including a missing database
                  file.  The caller is responsible for handling this as a
                  service-unavailable condition and must not make an LLM call.
    """
    db = _db_path()

    # Raise RAGError immediately if the database file does not exist so the
    # caller receives a clear error rather than a confusing sqlite3 message.
    if not os.path.isfile(db):
        raise RAGError(
            f"Knowledge base not found at '{db}'. "
            "Run 'python knowledge_base/seed.py' to create and populate it."
        )

    try:
        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT rowid, species_name, category, content "
                "FROM kb_fts "
                "WHERE kb_fts MATCH ? "
                "ORDER BY rank "
                "LIMIT ?",
                (query, top_k),
            )
            rows = cursor.fetchall()
    except sqlite3.Error as exc:
        raise RAGError(f"Database error during FTS5 retrieval: {exc}") from exc

    return [
        KBRecord(
            id=row["rowid"],
            species_name=row["species_name"],
            category=row["category"],
            content=row["content"],
        )
        for row in rows
    ]
