from typing import Any

from app.ai.verification.fact_checker import FactChecker


class HallucinationDetector:

    @classmethod
    def detect(
        cls,
        answer: str,
        context: str,
    ) -> dict[str, Any]:

        result = FactChecker.check(
            answer=answer,
            context=context,
        )

        unsupported = result[
            "unsupported_claims"
        ]

        claims = (
            result["verified_claims"]
            + unsupported
        )

        if not claims:

            return {
                "score": 0.0,
                "risk": "HIGH",
                "unsupported_claims": [],
            }

        unsupported_ratio = (
            len(unsupported) / len(claims)
        )

        if unsupported_ratio <= 0.10:
            risk = "LOW"

        elif unsupported_ratio <= 0.35:
            risk = "MEDIUM"

        else:
            risk = "HIGH"

        return {
            "score": round(
                unsupported_ratio,
                3,
            ),
            "risk": risk,
            "unsupported_claims": unsupported,
        }