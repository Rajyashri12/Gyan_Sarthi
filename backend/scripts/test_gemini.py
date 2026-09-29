from app.ai.gemini_client import GeminiClient


def main():

    client = GeminiClient()

    response = client.generate(
        "Explain database transaction in simple terms."
    )

    print("\n===== GEMINI RESPONSE =====\n")
    print(response)


if __name__ == "__main__":
    main()