import ast
from typing import Any


class CodeChecker:

    @staticmethod
    def extract_code_blocks(
        answer: str,
    ) -> list[str]:

        if not answer:
            return []

        blocks = []

        lines = answer.splitlines()

        inside = False
        current = []

        for line in lines:

            if line.strip().startswith("```"):

                if inside:
                    blocks.append(
                        "\n".join(current)
                    )

                    current = []
                    inside = False

                else:
                    inside = True

                continue

            if inside:
                current.append(line)

        return blocks

    @staticmethod
    def validate_python(
        code: str,
    ) -> tuple[bool, str]:

        try:

            ast.parse(code)

            return True, ""

        except SyntaxError as exc:

            return (
                False,
                f"Python syntax error: {exc}",
            )

    @classmethod
    def check(
        cls,
        answer: str,
    ) -> dict[str, Any]:

        code_blocks = cls.extract_code_blocks(
            answer
        )

        if not code_blocks:

            return {
                "score": 1.0,
                "code_blocks": 0,
                "issues": [],
            }

        issues = []

        valid_blocks = 0

        for code in code_blocks:

            valid, error = cls.validate_python(
                code
            )

            if valid:
                valid_blocks += 1
            else:
                issues.append(error)

        score = (
            valid_blocks / len(code_blocks)
        )

        return {
            "score": round(score, 3),
            "code_blocks": len(code_blocks),
            "issues": issues,
        }