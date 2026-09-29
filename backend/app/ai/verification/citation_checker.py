from typing import Any


class CitationChecker:

    @staticmethod
    def check(
        answer: str,
        sources: list[str],
        context: str,
    ) -> dict[str, Any]:

        if not answer:
            return {
                "score": 0.0,
                "issues": ["Empty AI response."],
            }

        # If there is retrieved evidence,
        # the answer has a verifiable evidence base.
        if sources and context:

            return {
                "score": 1.0,
                "issues": [],
            }

        if context:

            return {
                "score": 0.75,
                "issues": [
                    "Retrieved context exists but source metadata is unavailable."
                ],
            }

        return {
            "score": 0.0,
            "issues": [
                "No evidence source was retrieved."
            ],
        }