from app.ai.rag.ingestion import KnowledgeIngestion


def main():

    print("Starting Gyan Sarthi RAG ingestion...")

    ingestion = KnowledgeIngestion()

    ingestion.ingest()


if __name__ == "__main__":
    main()