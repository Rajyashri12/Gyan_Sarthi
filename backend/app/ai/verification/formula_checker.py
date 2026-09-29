import re
from typing import Any


class FormulaChecker:

    @staticmethod
    def extract_formulas(text: str) -> list[str]:
        """
        Detect common mathematical expressions.
        """

        if not text:
            return []

        patterns = [
            r"\b[A-Za-z]\s*=\s*[^,\n]+",
            r"\b\d+\s*[\+\-\*\/]\s*\d+\b",
            r"\b\d+\s*%\b",
            r"\b\d+\s*[xX]\s*\d+\b",
        ]

        formulas = []

        for pattern in patterns:
            matches = re.findall(
                pattern,
                text,
            )

            formulas.extend(matches)

        return list(set(formulas))

    @staticmethod
    def check(
        answer: str,
        context: str,
    ) -> dict[str, Any]:

        formulas = FormulaChecker.extract_formulas(
            answer
        )

        # No formulas means this checker
        # should not penalize the answer.
        if not formulas:
            return {
                "score": 1.0,
                "formulas": [],
                "issues": [],
            }

        issues = []

        context_lower = context.lower()

        supported = 0

        for formula in formulas:

            if formula.lower() in context_lower:
                supported += 1
            else:
                # Formula exists but could not be
                # directly found in retrieved evidence.
                issues.append(
                    f"Formula not directly supported by retrieved context: {formula}"
                )

        score = supported / len(formulas)

        return {
            "score": round(score, 3),
            "formulas": formulas,
            "issues": issues,
        }