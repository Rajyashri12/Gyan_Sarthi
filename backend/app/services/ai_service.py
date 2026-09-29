from app.ai.gemini_client import GeminiClient
from app.ai.rag.retriever import KnowledgeRetriever
from app.ai.prompts.tutor_prompts import build_tutor_prompt
from app.ai.verification.engine import VerificationEngine


class AIService:

    def __init__(self):

        self.retriever = KnowledgeRetriever()

        self.gemini = GeminiClient()

        self.verifier = VerificationEngine()

    def explain(
        self,
        question: str,
        subject_code: str | None = None,
        topic: str | None = None,
    ):

        # --------------------------------
        # STEP 1 — RETRIEVE
        # --------------------------------

        context = self.retriever.search(
            query=question,
            subject_code=subject_code,
            topic=topic,
            top_k=5,
        )

        # --------------------------------
        # STEP 2 — BUILD PROMPT
        # --------------------------------

        prompt = build_tutor_prompt(
            question=question,
            context=context,
            subject=subject_code,
            topic=topic,
        )

        # --------------------------------
        # STEP 3 — GENERATE
        # --------------------------------

        answer = self.gemini.generate(
            prompt
        )

        # --------------------------------
        # STEP 4 — VERIFY
        # --------------------------------

        verification = self.verifier.verify(
            answer=answer,
            context=context,
        )

        # --------------------------------
        # STEP 5 — FINAL RESPONSE
        # --------------------------------

        return {
            "question": question,
            "answer": answer,
            "verification": verification,
            "sources": context,
        }