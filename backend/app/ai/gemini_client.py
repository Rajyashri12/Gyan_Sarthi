import time
from google import genai

from app.core.config import settings


class GeminiClient:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        # Primary model
        self.primary_model = "gemini-3.6-flash"

        # Fallback model
        self.fallback_model = "gemini-2.5-flash"

    def _generate(self, model: str, prompt: str) -> str:

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            raise ValueError(
                f"Gemini returned an empty response using {model}."
            )

        return text

    def generate(self, prompt: str) -> str:

        last_error = None

        # -----------------------------------------
        # PRIMARY MODEL
        # -----------------------------------------

        for attempt in range(3):

            try:

                print(
                    f"Gemini primary attempt "
                    f"{attempt + 1}/3: {self.primary_model}"
                )

                return self._generate(
                    self.primary_model,
                    prompt,
                )

            except Exception as exc:

                last_error = exc

                print(
                    f"Gemini primary attempt "
                    f"{attempt + 1} failed:"
                )

                print(type(exc).__name__)
                print(str(exc))

                # Wait before retry
                if attempt < 2:
                    time.sleep(2 ** attempt)

        # -----------------------------------------
        # FALLBACK MODEL
        # -----------------------------------------

        print(
            f"Primary model unavailable. "
            f"Trying fallback: {self.fallback_model}"
        )

        for attempt in range(2):

            try:

                print(
                    f"Gemini fallback attempt "
                    f"{attempt + 1}/2: {self.fallback_model}"
                )

                return self._generate(
                    self.fallback_model,
                    prompt,
                )

            except Exception as exc:

                last_error = exc

                print(
                    f"Gemini fallback attempt "
                    f"{attempt + 1} failed:"
                )

                print(type(exc).__name__)
                print(str(exc))

                if attempt < 1:
                    time.sleep(2)

        # -----------------------------------------
        # ALL ATTEMPTS FAILED
        # -----------------------------------------

        raise RuntimeError(
            "Gemini generation failed after multiple attempts. "
            f"Last error: {last_error}"
        )