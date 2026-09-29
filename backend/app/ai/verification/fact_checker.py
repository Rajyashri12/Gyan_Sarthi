from typing import Any


class FactChecker:
    """
    Checks whether an AI-generated answer is supported
    by retrieved knowledge-base context.

    This is an evidence-based checker:
    
        Answer
          ↓
        Claims
          ↓
    Compare with retrieved context
          ↓
    Supported / Unsupported
    """

    @staticmethod
    def normalize(text: str) -> str:
        return " ".join(
            text.lower().strip().split()
        )

    @staticmethod
    def extract_claims(answer: str) -> list[str]:
        """
        Lightweight claim extraction.

        For MVP, each meaningful sentence is treated
        as a potential factual claim.
        """

        if not answer:
            return []

        sentences = []

        for sentence in answer.replace("\n", " ").split("."):
            sentence = sentence.strip()

            if len(sentence) >= 15:
                sentences.append(sentence)

        return sentences

    @staticmethod
    def calculate_support(
        claim: str,
        context: str,
    ) -> float:
        """
        Estimate whether the claim is supported by context.

        Uses token overlap as an MVP evidence check.
        """

        if not claim or not context:
            return 0.0

        claim_words = set(
            FactChecker.normalize(claim).split()
        )

        context_words = set(
            FactChecker.normalize(context).split()
        )

        if not claim_words:
            return 0.0

        overlap = claim_words.intersection(
            context_words
        )

        score = len(overlap) / len(claim_words)

        return min(1.0, score)

    @classmethod
    def check(
        cls,
        answer: str,
        context: str,
    ) -> dict[str, Any]:

        claims = cls.extract_claims(answer)

        if not claims:
            return {
                "score": 0.0,
                "verified_claims": [],
                "unsupported_claims": [],
            }

        verified_claims = []
        unsupported_claims = []

        scores = []

        for claim in claims:

            support = cls.calculate_support(
                claim,
                context,
            )

            scores.append(support)

            if support >= 0.45:
                verified_claims.append(claim)
            else:
                unsupported_claims.append(claim)

        score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        return {
            "score": round(score, 3),
            "verified_claims": verified_claims,
            "unsupported_claims": unsupported_claims,
        }