# backend/app/ai/rag/retriever.py

from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATH CONFIGURATION
# ============================================================

# File location:
#
# Gyan-Sarthi/
# ├── backend/
# │   └── app/
# │       └── ai/
# │           └── rag/
# │               └── retriever.py
# │
# └── knowledge_base/
#     └── vector_db/
#
# parents[4] -> Gyan-Sarthi

BASE_DIR = Path(__file__).resolve().parents[4]

VECTOR_DB = (
    BASE_DIR
    / "knowledge_base"
    / "vector_db"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

COLLECTION_NAME = "gate_knowledge"

DEFAULT_TOP_K = 5


# ============================================================
# RAG RETRIEVER
# ============================================================

class RAGRetriever:
    """
    Gyan Sarthi Retrieval-Augmented Generation Retriever.

    Responsibilities:

        1. Load ChromaDB
        2. Load embedding model
        3. Convert student query into embedding
        4. Search relevant knowledge
        5. Apply subject/topic filters
        6. Return clean evidence objects

    Supported subjects:

        GA
        DBMS
        OS
        CN
    """

    def __init__(self):

        # ----------------------------------------------------
        # Vector database path
        # ----------------------------------------------------

        self.vector_db_path = VECTOR_DB

        # ----------------------------------------------------
        # Validate vector DB parent
        # ----------------------------------------------------

        self.vector_db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # Initialize ChromaDB
        # ----------------------------------------------------

        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_path)
        )

        # ----------------------------------------------------
        # Load knowledge collection
        # ----------------------------------------------------

        self.collection = (
            self.client.get_or_create_collection(
                name=COLLECTION_NAME
            )
        )

        # ----------------------------------------------------
        # Load embedding model
        # ----------------------------------------------------

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    # ========================================================
    # CREATE QUERY EMBEDDING
    # ========================================================

    def create_embedding(
        self,
        query: str,
    ) -> list[float]:

        """
        Convert a text query into an embedding vector.
        """

        if not query:

            return []

        query = str(query).strip()

        if not query:

            return []

        embedding = self.model.encode(
            query,
            show_progress_bar=False
        )

        return embedding.tolist()

    # ========================================================
    # BUILD FILTER
    # ========================================================

    @staticmethod
    def build_filter(
        subject_code: str | None = None,
        topic_id: int | None = None,
    ) -> dict | None:

        """
        Build ChromaDB metadata filter.

        Current ingestion metadata contains:

            exam
            subject
            subject_code
            topic
            source_file
            chunk_index

        topic_id is supported only when it exists
        in the stored metadata.
        """

        filters = []

        # ----------------------------------------------------
        # Subject filter
        # ----------------------------------------------------

        if subject_code:

            subject_code = (
                str(subject_code)
                .strip()
                .upper()
            )

            filters.append(
                {
                    "subject_code": subject_code
                }
            )

        # ----------------------------------------------------
        # Topic filter
        # ----------------------------------------------------

        if topic_id is not None:

            filters.append(
                {
                    "topic_id": str(topic_id)
                }
            )

        # ----------------------------------------------------
        # No filters
        # ----------------------------------------------------

        if not filters:

            return None

        # ----------------------------------------------------
        # Single filter
        # ----------------------------------------------------

        if len(filters) == 1:

            return filters[0]

        # ----------------------------------------------------
        # Multiple filters
        # ----------------------------------------------------

        return {
            "$and": filters
        }

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        subject_code: str | None = None,
        topic_id: int | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:

        """
        Search the Gyan Sarthi knowledge base.

        Parameters
        ----------
        query:
            Student's question.

        subject_code:
            Optional subject filter.

            Examples:
                GA
                DBMS
                OS
                CN

        topic_id:
            Optional PostgreSQL topic ID.

        top_k:
            Number of evidence chunks to retrieve.

        Returns
        -------
        list[dict]

            Each result contains:

                text
                content
                document
                metadata
                source
                source_file
                filename
                subject_code
                topic
                topic_id
                distance
        """

        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if not query:

            return []

        query = str(query).strip()

        if not query:

            return []

        # ----------------------------------------------------
        # Validate top_k
        # ----------------------------------------------------

        try:

            top_k = int(top_k)

        except (
            ValueError,
            TypeError
        ):

            top_k = DEFAULT_TOP_K

        top_k = max(
            1,
            min(top_k, 20)
        )

        # ----------------------------------------------------
        # Check collection
        # ----------------------------------------------------

        try:

            collection_count = (
                self.collection.count()
            )

        except Exception as exc:

            print(
                f"RAG collection error: {exc}"
            )

            return []

        if collection_count == 0:

            print(
                "RAG knowledge collection is empty."
            )

            return []

        # ----------------------------------------------------
        # Create embedding
        # ----------------------------------------------------

        try:

            query_embedding = (
                self.create_embedding(
                    query
                )
            )

        except Exception as exc:

            print(
                f"Embedding generation failed: {exc}"
            )

            return []

        if not query_embedding:

            return []

        # ----------------------------------------------------
        # Build metadata filter
        # ----------------------------------------------------

        where = self.build_filter(
            subject_code=subject_code,
            topic_id=topic_id,
        )

        # ----------------------------------------------------
        # Search ChromaDB
        # ----------------------------------------------------

        try:

            if where:

                results = (
                    self.collection.query(
                        query_embeddings=[
                            query_embedding
                        ],
                        n_results=min(
                            top_k,
                            collection_count
                        ),
                        where=where,
                    )
                )

            else:

                results = (
                    self.collection.query(
                        query_embeddings=[
                            query_embedding
                        ],
                        n_results=min(
                            top_k,
                            collection_count
                        ),
                    )
                )

        except Exception as exc:

            # ------------------------------------------------
            # Topic ID may not exist in current metadata.
            #
            # In that case, retry using subject only.
            # ------------------------------------------------

            if (
                topic_id is not None
                and subject_code
            ):

                print(
                    "Topic filter unavailable. "
                    "Retrying RAG search with subject filter."
                )

                try:

                    subject_where = {
                        "subject_code": (
                            str(subject_code)
                            .strip()
                            .upper()
                        )
                    }

                    results = (
                        self.collection.query(
                            query_embeddings=[
                                query_embedding
                            ],
                            n_results=min(
                                top_k,
                                collection_count
                            ),
                            where=subject_where,
                        )
                    )

                except Exception as retry_exc:

                    print(
                        f"RAG search failed: "
                        f"{retry_exc}"
                    )

                    return []

            else:

                print(
                    f"RAG search failed: {exc}"
                )

                return []

        # ====================================================
        # EXTRACT CHROMA RESULTS
        # ====================================================

        documents = results.get(
            "documents",
            [[]]
        )

        metadatas = results.get(
            "metadatas",
            [[]]
        )

        distances = results.get(
            "distances",
            [[]]
        )

        # ----------------------------------------------------
        # Chroma returns nested lists
        # ----------------------------------------------------

        if documents:

            documents = documents[0] or []

        else:

            documents = []

        if metadatas:

            metadatas = metadatas[0] or []

        else:

            metadatas = []

        if distances:

            distances = distances[0] or []

        else:

            distances = []

        # ----------------------------------------------------
        # No results
        # ----------------------------------------------------

        if not documents:

            return []

        # ====================================================
        # BUILD CLEAN RESULTS
        # ====================================================

        retrieved: list[
            dict[str, Any]
        ] = []

        for index, document in enumerate(
            documents
        ):

            # ------------------------------------------------
            # Metadata
            # ------------------------------------------------

            metadata: dict[str, Any] = {}

            if index < len(
                metadatas
            ):

                raw_metadata = (
                    metadatas[index]
                )

                if isinstance(
                    raw_metadata,
                    dict
                ):

                    metadata = raw_metadata

            # ------------------------------------------------
            # Distance
            # ------------------------------------------------

            distance = None

            if index < len(
                distances
            ):

                distance = distances[
                    index
                ]

            # ------------------------------------------------
            # Source
            #
            # Your metadata.py stores:
            #
            # "source_file": path.name
            #
            # Therefore source must fall back
            # to source_file.
            # ------------------------------------------------

            source = (
                metadata.get("source")
                or metadata.get(
                    "source_file"
                )
                or metadata.get(
                    "filename"
                )
                or metadata.get(
                    "file"
                )
            )

            # ------------------------------------------------
            # Topic
            # ------------------------------------------------

            topic = metadata.get(
                "topic"
            )

            # ------------------------------------------------
            # Subject
            # ------------------------------------------------

            retrieved_subject_code = (
                metadata.get(
                    "subject_code"
                )
            )

            # ------------------------------------------------
            # Topic ID
            # ------------------------------------------------

            retrieved_topic_id = (
                metadata.get(
                    "topic_id"
                )
            )

            # ------------------------------------------------
            # Build result
            # ------------------------------------------------

            result = {
                "text": document,
                "content": document,
                "document": document,

                "metadata": metadata,

                "source": source,
                "source_file": source,
                "filename": source,

                "subject": metadata.get(
                    "subject"
                ),

                "subject_code": (
                    retrieved_subject_code
                ),

                "topic": topic,
                "topic_id": (
                    retrieved_topic_id
                ),
                "topic_slug": metadata.get("topic_slug"),

                "exam": metadata.get(
                    "exam"
                ),

                "chunk_index": metadata.get(
                    "chunk_index"
                ),

                "distance": distance,
            }

            retrieved.append(
                result
            )

        return retrieved

    # ========================================================
    # RETRIEVE ALIAS
    # ========================================================

    def retrieve(
        self,
        query: str,
        subject_code: str | None = None,
        topic_id: int | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:

        """
        Alias for search().
        """

        return self.search(
            query=query,
            subject_code=subject_code,
            topic_id=topic_id,
            top_k=top_k,
        )

    # ========================================================
    # QUERY ALIAS
    # ========================================================

    def query(
        self,
        query: str,
        subject_code: str | None = None,
        topic_id: int | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:

        """
        Alias for search().
        """

        return self.search(
            query=query,
            subject_code=subject_code,
            topic_id=topic_id,
            top_k=top_k,
        )

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health_check(self) -> dict[str, Any]:

        """
        Return basic RAG system status.
        """

        try:

            count = self.collection.count()

            return {
                "status": "ok",
                "collection": (
                    self.collection.name
                ),
                "document_count": count,
                "vector_db": str(
                    self.vector_db_path
                ),
                "embedding_model": (
                    EMBEDDING_MODEL
                ),
            }

        except Exception as exc:

            return {
                "status": "error",
                "collection": (
                    COLLECTION_NAME
                ),
                "document_count": 0,
                "vector_db": str(
                    self.vector_db_path
                ),
                "embedding_model": (
                    EMBEDDING_MODEL
                ),
                "error": str(exc),
            }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GYAN SARTHI RAG RETRIEVER TEST")
    print("=" * 60)

    retriever = RAGRetriever()

    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------

    health = retriever.health_check()

    print("\nRAG HEALTH")
    print("-" * 60)

    for key, value in health.items():

        print(
            f"{key}: {value}"
        )

    # --------------------------------------------------------
    # Test DBMS retrieval
    # --------------------------------------------------------

    print("\nDBMS TEST")
    print("-" * 60)

    results = retriever.search(
        query=(
            "What is normalization "
            "in DBMS?"
        ),
        subject_code="DBMS",
        top_k=5,
    )

    print(
        f"Results: {len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n[{index}]"
        )

        print(
            "Source:",
            result.get("source")
        )

        print(
            "Subject:",
            result.get(
                "subject_code"
            )
        )

        print(
            "Topic:",
            result.get(
                "topic"
            )
        )

        print(
            "Distance:",
            result.get(
                "distance"
            )
        )

        print(
            "Text:",
            result.get(
                "text",
                ""
            )[:300]
        )