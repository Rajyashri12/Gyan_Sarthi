from app.ai.rag.retriever import KnowledgeRetriever


def main():

    retriever = KnowledgeRetriever()

    results = retriever.search(
        query="What is second normal form?",
        subject_code="DBMS",
        top_k=3,
    )

    print("\n===== RAG RESULTS =====\n")

    for index, result in enumerate(results, 1):

        print(f"Result {index}")

        print(
            "Subject:",
            result["metadata"]["subject"]
        )

        print(
            "Topic:",
            result["metadata"]["topic"]
        )

        print(
            "Distance:",
            result["distance"]
        )

        print(
            "Content:",
            result["content"]
        )

        print("\n----------------------\n")


if __name__ == "__main__":
    main()