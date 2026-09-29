from typing import Any

from app.ai.verification.fact_checker import FactChecker
from app.ai.verification.formula_checker import FormulaChecker
from app.ai.verification.code_checker import CodeChecker
from app.ai.verification.citation_checker import CitationChecker
from app.ai.verification.hallucination_detector import (
    HallucinationDetector,
)


class VerificationEngine:
    """
    Gyan Sarthi AI Verification Engine.

    Pipeline:

        AI Answer
             ↓
        Fact Check
             ↓
        Formula Check
             ↓
        Code Check
             ↓
        Citation Check
             ↓
        Hallucination Detection
             ↓
        Confidence Calculation
             ↓
        Verification Status
    """

    @staticmethod
    def calculate_confidence(
        fact_score: float,
        formula_score: float,
        code_score: float,
        citation_score: float,
        hallucination_score: float,
    ) -> float:

        # Hallucination is a risk score,
        # therefore convert it to safety.
        hallucination_safety = (
            1.0 - hallucination_score
        )

        confidence = (
            fact_score * 0.35
            + formula_score * 0.15
            + code_score * 0.10
            + citation_score * 0.15
            + hallucination_safety * 0.25
        )

        return round(
            max(0.0, min(1.0, confidence)),
            3,
        )

    @staticmethod
    def determine_status(
        confidence: float,
    ) -> str:

        if confidence >= 0.85:
            return "VERIFIED"

        if confidence >= 0.60:
            return "PARTIALLY_VERIFIED"

        return "LOW_CONFIDENCE"

    @classmethod
    def verify(
        cls,
        answer: str,
        context: str = "",
        sources: list[str] | None = None,
    ) -> dict[str, Any]:

        if sources is None:
            sources = []

        issues: list[str] = []

        # ---------------------------------------------------------
        # 1. FACT VERIFICATION
        # ---------------------------------------------------------

        fact_result = FactChecker.check(
            answer=answer,
            context=context,
        )

        fact_score = fact_result["score"]

        unsupported_claims = fact_result[
            "unsupported_claims"
        ]

        if unsupported_claims:

            issues.append(
                f"{len(unsupported_claims)} claim(s) "
                "could not be supported by retrieved evidence."
            )

        # ---------------------------------------------------------
        # 2. FORMULA VERIFICATION
        # ---------------------------------------------------------

        formula_result = FormulaChecker.check(
            answer=answer,
            context=context,
        )

        formula_score = formula_result["score"]

        issues.extend(
            formula_result.get(
                "issues",
                [],
            )
        )

        # ---------------------------------------------------------
        # 3. CODE VERIFICATION
        # ---------------------------------------------------------

        code_result = CodeChecker.check(
            answer=answer,
        )

        code_score = code_result["score"]

        issues.extend(
            code_result.get(
                "issues",
                [],
            )
        )

        # ---------------------------------------------------------
        # 4. CITATION VERIFICATION
        # ---------------------------------------------------------

        citation_result = CitationChecker.check(
            answer=answer,
            sources=sources,
            context=context,
        )

        citation_score = citation_result[
            "score"
        ]

        issues.extend(
            citation_result.get(
                "issues",
                [],
            )
        )

        # ---------------------------------------------------------
        # 5. HALLUCINATION DETECTION
        # ---------------------------------------------------------

        hallucination_result = (
            HallucinationDetector.detect(
                answer=answer,
                context=context,
            )
        )

        hallucination_score = (
            hallucination_result["score"]
        )

        # ---------------------------------------------------------
        # 6. CONFIDENCE
        # ---------------------------------------------------------

        confidence = cls.calculate_confidence(
            fact_score=fact_score,
            formula_score=formula_score,
            code_score=code_score,
            citation_score=citation_score,
            hallucination_score=hallucination_score,
        )

        # ---------------------------------------------------------
        # 7. STATUS
        # ---------------------------------------------------------

        status = cls.determine_status(
            confidence
        )

        # ---------------------------------------------------------
        # 8. Add status-specific warnings
        # ---------------------------------------------------------

        if status == "LOW_CONFIDENCE":

            issues.append(
                "The generated answer has low "
                "evidence confidence and should be "
                "reviewed before being treated as reliable."
            )

        elif status == "PARTIALLY_VERIFIED":

            issues.append(
                "Some parts of the generated answer "
                "could not be fully verified."
            )

        return {
            "fact_score": fact_score,
            "formula_score": formula_score,
            "code_score": code_score,
            "citation_score": citation_score,
            "hallucination_score": hallucination_score,
            "confidence_score": confidence,
            "status": status,
            "issues": list(dict.fromkeys(issues)),
            "verified_claims": fact_result[
                "verified_claims"
            ],
            "unsupported_claims": unsupported_claims,
        }