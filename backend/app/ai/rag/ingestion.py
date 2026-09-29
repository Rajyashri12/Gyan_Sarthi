from pathlib import Path
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from app.ai.rag.metadata import extract_metadata


BASE_DIR = Path(__file__).resolve().parents[4]

KNOWLEDGE_BASE = BASE_DIR / "knowledge_base" / "gate"
VECTOR_DB = BASE_DIR / "knowledge_base" / "vector_db"


EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class KnowledgeIngestion:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB)
        )

        self.collection = self.client.get_or_create_collection(
            name="gate_knowledge"
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    def read_file(self, file_path: Path) -> str:

        if file_path.suffix.lower() in [".md", ".txt"]:
            return file_path.read_text(
                encoding="utf-8"
            )

        if file_path.suffix.lower() == ".pdf":

            from pypdf import PdfReader

            reader = PdfReader(str(file_path))

            pages = []

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    pages.append(text)

            return "\n".join(pages)

        return ""

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        overlap: int = 120
    ):

        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def generate_id(
        self,
        file_path: Path,
        chunk_index: int
    ):

        raw = f"{file_path}:{chunk_index}"

        return hashlib.md5(
            raw.encode()
        ).hexdigest()

    def ingest(self):

        files = []

        for extension in ["*.md", "*.txt", "*.pdf"]:
            files.extend(
                KNOWLEDGE_BASE.rglob(extension)
            )

        total_chunks = 0

        for file_path in files:

            text = self.read_file(file_path)

            chunks = self.chunk_text(text)

            if not chunks:
                continue

            metadata = extract_metadata(
                str(file_path)
            )

            embeddings = self.model.encode(
                chunks,
                show_progress_bar=False
            )

            ids = []
            metadatas = []

            for index, chunk in enumerate(chunks):

                ids.append(
                    self.generate_id(
                        file_path,
                        index
                    )
                )

                metadatas.append(
                    {
                        **metadata,
                        "chunk_index": index,
                    }
                )

            self.collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
            )

            total_chunks += len(chunks)

            print(
                f"Ingested: {file_path} "
                f"({len(chunks)} chunks)"
            )

        print(
            f"\nRAG ingestion completed."
        )

        print(
            f"Total chunks: {total_chunks}"
        )


if __name__ == "__main__":
    ingestion = KnowledgeIngestion()
    ingestion.ingest()