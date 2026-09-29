from app.services.ai_service import AIService


def main():

    service = AIService()

    result = service.explain(
        question="What is 2NF and what problem does it solve?",
        subject_code="DBMS",
        topic="normalization",
    )

    print("\n==============================")
    print("GYAN SARTHI AI TUTOR")
    print("==============================\n")

    print("QUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:

        metadata = source["metadata"]

        print(
            f"- {metadata.get('subject')} "
            f"| {metadata.get('topic')} "
            f"| {metadata.get('source_file')}"
        )


if __name__ == "__main__":
    main()