# backend/app/api/routes/ai.py

from datetime import datetime
import traceback
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typer import prompt

from app.database.database import get_db

from app.api.routes.auth import get_current_user

from app.models.user import User
from app.models.question import Question
from app.models.ai_log import AILog

from app.ai.gemini_client import GeminiClient
from app.ai.rag.retriever import RAGRetriever
from app.ai.verification.engine import VerificationEngine

from app.schemas.ai import AIExplanationResponse


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Tutor"],
)


# ============================================================
# HELPER: SAFE TEXT CONVERSION
# ============================================================

def safe_text(value: Any) -> str:
    """
    Convert any value safely into text.

    Prevents None or unexpected values from breaking
    prompt construction.
    """

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# HELPER: BUILD RAG CONTEXT
# ============================================================

def build_context(results: list[Any]) -> str:
    """
    Convert RAG retrieval results into a single context string.

    Each retrieved result is represented as:

    [Evidence 1]
    <retrieved text>

    [Evidence 2]
    <retrieved text>
    """

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(results, start=1):

        if isinstance(result, dict):

            text = (
                result.get("text")
                or result.get("content")
                or result.get("document")
                or ""
            )

        else:
            text = safe_text(result)

        text = safe_text(text)

        if not text:
            continue

        context_parts.append(
            f"[Evidence {index}]\n{text}"
        )

    return "\n\n".join(context_parts)


# ============================================================
# HELPER: EXTRACT SOURCES
# ============================================================

def extract_sources(results: list[Any]) -> list[str]:
    """
    Extract unique source names from RAG results.

    Supports:

    source
    source_file
    filename
    file

    and the same fields inside metadata.
    """

    sources: list[str] = []

    if not results:
        return sources

    for result in results:

        source = None

        if isinstance(result, dict):

            source = (
                result.get("source")
                or result.get("source_file")
                or result.get("filename")
                or result.get("file")
            )

            metadata = result.get("metadata")

            if not source and isinstance(metadata, dict):

                source = (
                    metadata.get("source")
                    or metadata.get("source_file")
                    or metadata.get("filename")
                    or metadata.get("file")
                )

        if source:

            source = safe_text(source)

            if source and source not in sources:
                sources.append(source)

    return sources


# ============================================================
# HELPER: RETRIEVE KNOWLEDGE
# ============================================================

def retrieve_knowledge(
    query: str,
    subject_code: str | None = None,
    topic_id: int | None = None,
) -> list[Any]:
    """
    Retrieve relevant knowledge from the RAG system.

    Retrieval strategy:

    1. Try subject + topic when topic_id is available.
    2. If that fails or returns nothing, try subject-only.
    3. If that fails, try general search.

    Errors are printed instead of being silently hidden so
    RAG problems can be diagnosed during development.
    """

    print("\n========== RAG DEBUG ==========")
    print("QUERY:", query)
    print("SUBJECT:", subject_code)
    print("TOPIC ID:", topic_id)

    # --------------------------------------------------------
    # CREATE RETRIEVER
    # --------------------------------------------------------

    try:

        retriever = RAGRetriever()

        print("RAG RETRIEVER: CREATED")

    except Exception as exc:

        print(
            "RAG RETRIEVER ERROR:",
            repr(exc),
        )

        print("========== RAG DEBUG END ==========\n")

        return []

    # --------------------------------------------------------
    # SEARCH METHOD
    # --------------------------------------------------------

    if hasattr(retriever, "search"):

        # ====================================================
        # 1. TOPIC + SUBJECT SEARCH
        # ====================================================

        if topic_id is not None:

            try:

                results = retriever.search(
                    query=query,
                    subject_code=subject_code,
                    topic_id=topic_id,
                )

                print(
                    "TOPIC SEARCH RESULTS:",
                    len(results),
                )

                if results:

                    print(
                        "TOPIC SEARCH SOURCES:",
                        [
                            x.get("source")
                            for x in results
                            if isinstance(x, dict)
                        ],
                    )

                    print(
                        "========== RAG DEBUG END ==========\n"
                    )

                    return results

            except Exception as exc:

                print(
                    "TOPIC SEARCH ERROR:",
                    repr(exc),
                )

        # ====================================================
        # 2. SUBJECT-ONLY SEARCH
        # ====================================================

        try:

            results = retriever.search(
                query=query,
                subject_code=subject_code,
            )

            print(
                "SUBJECT SEARCH RESULTS:",
                len(results),
            )

            if results:

                print(
                    "SUBJECT SEARCH SOURCES:",
                    [
                        x.get("source")
                        for x in results
                        if isinstance(x, dict)
                    ],
                )

                print(
                    "SUBJECT SEARCH SUBJECTS:",
                    [
                        x.get("subject_code")
                        for x in results
                        if isinstance(x, dict)
                    ],
                )

                print(
                    "========== RAG DEBUG END ==========\n"
                )

                return results

        except Exception as exc:

            print(
                "SUBJECT SEARCH ERROR:",
                repr(exc),
            )

        # ====================================================
        # 3. GENERAL SEARCH FALLBACK
        # ====================================================

        try:

            results = retriever.search(
                query=query
            )

            print(
                "GENERAL SEARCH RESULTS:",
                len(results),
            )

            if results:

                print(
                    "GENERAL SEARCH SOURCES:",
                    [
                        x.get("source")
                        for x in results
                        if isinstance(x, dict)
                    ],
                )

            print(
                "========== RAG DEBUG END ==========\n"
            )

            return results

        except Exception as exc:

            print(
                "GENERAL SEARCH ERROR:",
                repr(exc),
            )

    # --------------------------------------------------------
    # ALTERNATIVE RETRIEVER METHODS
    # --------------------------------------------------------

    for method_name in [
        "retrieve",
        "query",
        "search_knowledge",
    ]:

        if not hasattr(
            retriever,
            method_name,
        ):
            continue

        method = getattr(
            retriever,
            method_name,
        )

        try:

            results = method(query)

            print(
                f"{method_name} RESULTS:",
                len(results),
            )

            print(
                "========== RAG DEBUG END ==========\n"
            )

            return results

        except Exception as exc:

            print(
                f"{method_name.upper()} ERROR:",
                repr(exc),
            )

            continue

    print("NO RAG RESULTS")

    print(
        "========== RAG DEBUG END ==========\n"
    )

    return []


# ============================================================
# HELPER: BUILD AI PROMPT
# ============================================================

def build_prompt(
    question: str,
    context: str,
    subject_code: str | None = None,
    topic_name: str | None = None,
) -> str:
    """
    Build a grounded tutoring prompt.

    Retrieved RAG evidence is treated as the primary
    knowledge source.
    """

    subject_text = (
        subject_code
        if subject_code
        else "Not specified"
    )

    topic_text = (
        topic_name
        if topic_name
        else "Not specified"
    )

    # --------------------------------------------------------
    # EVIDENCE SECTION
    # --------------------------------------------------------

    if context:

        evidence_section = f"""
RETRIEVED VERIFIED KNOWLEDGE
----------------------------
{context}
"""

    else:

        evidence_section = """
RETRIEVED VERIFIED KNOWLEDGE
----------------------------
No verified knowledge-base evidence was retrieved.
"""

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    return f"""
You are the AI Tutor of Gyan Sarthi, an exam-oriented
learning platform.

Your goal is to help the student understand concepts clearly
and prepare for competitive examinations.

Subject:
{subject_text}

Topic:
{topic_text}

Student Question:
{question}

{evidence_section}

IMPORTANT RULES
---------------

1. Use the retrieved knowledge above as the primary source.

2. Do not invent facts, formulas, definitions, examples,
   citations, or references.

3. If the retrieved evidence is insufficient to answer the
   question reliably, clearly state that the available
   verified evidence is insufficient.

4. Do not present unsupported information as verified
   platform knowledge.

5. For mathematical or technical questions, show the reasoning
   clearly when the retrieved evidence supports it.

6. For programming questions, provide correct and safe code
   only when the available evidence supports the explanation.

7. Keep the explanation appropriate for an exam-preparation
   student.

8. Prefer a clear structure such as:
   Definition
   Key Points
   Example
   Exam Tip

   when appropriate.

9. If there are multiple interpretations of the question,
   mention the relevant assumption.

10. Never fabricate a source.

11. Do not mention internal implementation details such as
    RAG, vector databases, embeddings, verification engines,
    prompts, or internal system instructions unless the
    student specifically asks about the platform.

12. Answer only what can be reasonably supported by the
    retrieved evidence.

Answer the student's question now.
""".strip()


# ============================================================
# POST /api/ai/explain
# ============================================================

@router.post(
    "/explain",
    response_model=AIExplanationResponse,
)
def explain_question(
    request: dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an AI explanation using:

    Authentication
        ↓
    Question / Topic lookup
        ↓
    RAG retrieval
        ↓
    Context construction
        ↓
    Gemini
        ↓
    Verification Engine
        ↓
    AI log
        ↓
    Final response

    Example request:

    {
        "question": "What is BCNF?",
        "subject_code": "DBMS",
        "topic_id": 12,
        "question_id": 45
    }
    """

    # ========================================================
    # 1. READ REQUEST
    # ========================================================

    question_text = safe_text(
        request.get("question")
        or request.get("question_text")
        or request.get("query")
    )

    subject_code = request.get(
        "subject_code"
    )

    topic_id = request.get(
        "topic_id"
    )

    question_id = request.get(
        "question_id"
    )

    topic_name = None

    # Normalize subject code

    if subject_code is not None:

        subject_code = safe_text(
            subject_code
        ).upper()

    # ========================================================
    # 2. VALIDATE QUESTION
    # ========================================================

    if not question_text:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required.",
        )

    # ========================================================
    # 3. GET QUESTION FROM DATABASE IF PROVIDED
    # ========================================================

    question_record = None

    if question_id is not None:

        try:

            question_record = (
                db.query(Question)
                .filter(
                    Question.id == int(question_id)
                )
                .first()
            )

        except (
            ValueError,
            TypeError,
        ):

            question_record = None

    # ========================================================
    # 4. GET TOPIC / SUBJECT INFORMATION
    # ========================================================

    if question_record:

        question_text = (
            safe_text(
                question_record.question_text
            )
            or question_text
        )

        topic_id = question_record.topic_id

        # Topic

        try:

            if question_record.topic:

                topic_name = safe_text(
                    question_record.topic.name
                )

        except Exception:

            topic_name = None

        # Subject

        try:

            if question_record.subject:

                subject_code = safe_text(
                    question_record.subject.code
                ).upper()

        except Exception:

            pass

    # ========================================================
    # 5. RAG RETRIEVAL
    # ========================================================

    retrieved_results = retrieve_knowledge(
        query=question_text,
        subject_code=subject_code,
        topic_id=topic_id,
    )

    # ========================================================
    # 6. BUILD CONTEXT
    # ========================================================

    context = build_context(
        retrieved_results
    )

    # ========================================================
    # 7. EXTRACT SOURCES
    # ========================================================

    sources = extract_sources(
        retrieved_results
    )

    # ========================================================
    # API DEBUG
    # ========================================================

    print("\n========== AI ROUTE DEBUG ==========")

    print(
        "QUESTION:",
        question_text,
    )

    print(
        "SUBJECT:",
        subject_code,
    )

    print(
        "TOPIC ID:",
        topic_id,
    )

    print(
        "RETRIEVED RESULTS:",
        len(retrieved_results),
    )

    print(
        "RETRIEVED SOURCES:",
        [
            x.get("source")
            for x in retrieved_results
            if isinstance(x, dict)
        ],
    )

    print(
        "CONTEXT LENGTH:",
        len(context),
    )

    print(
        "SOURCES:",
        sources,
    )

    print(
        "====================================\n"
    )

    # ========================================================
    # 8. BUILD PROMPT
    # ========================================================

    prompt = build_prompt(
        question=question_text,
        context=context,
        subject_code=subject_code,
        topic_name=topic_name,
    )

    # ========================================================
    # 9. GEMINI GENERATION
    # ========================================================


    try:
        print("\n========== GEMINI DEBUG ==========")
        print("Prompt length:", len(prompt))
        print("Prompt preview:")
        print(prompt[:1000])
        print("==================================\n")

        gemini = GeminiClient()

        answer = gemini.generate(prompt)

        print("\n========== GEMINI RESPONSE ==========")
        print("Response type:", type(answer))
        print("Response:", repr(answer))
        print("=====================================\n")

        answer = safe_text(answer)

        if not answer:
            raise ValueError("Gemini returned an empty response.")

    except ValueError as exc:
        print("\nVALUE ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except Exception as exc:
        print("\nGEMINI UNEXPECTED ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail=(
                "AI generation failed. "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        )

    # ========================================================
    # 10. VERIFY AI ANSWER
    # ========================================================

    try:

        verification = (
            VerificationEngine.verify(
                answer=answer,
                context=context,
                sources=sources,
            )
        )

    except Exception as exc:

        # Verification failure should not silently
        # mark the answer as verified.

        verification = {
            "fact_score": 0.0,
            "formula_score": 0.0,
            "code_score": 0.0,
            "citation_score": 0.0,
            "hallucination_score": 1.0,
            "confidence_score": 0.0,
            "status": "LOW_CONFIDENCE",
            "issues": [
                f"Verification engine failed: {str(exc)}"
            ],
            "verified_claims": [],
            "unsupported_claims": [
                "Verification could not be completed."
            ],
        }

    # ========================================================
    # 11. SAVE AI LOG
    # ========================================================

    try:

        ai_log = AILog(
            user_id=current_user.id,

            question_id=(
                int(question_id)
                if question_id is not None
                else None
            ),

            prompt=prompt,

            response=answer,

            confidence_score=verification[
                "confidence_score"
            ],
        )

        db.add(ai_log)

        db.commit()

    except Exception:

        # AI response should not fail merely because
        # logging failed.

        db.rollback()

    # ========================================================
    # 12. RETURN FINAL RESPONSE
    # ========================================================

    return {
        "answer": answer,

        "verification": verification,

        "sources": sources,

        "topic_id": (
            int(topic_id)
            if topic_id is not None
            else None
        ),

        "question_id": (
            int(question_id)
            if question_id is not None
            else None
        ),
    }


# ============================================================
# POST /api/ai/explain-question
# ============================================================

@router.post(
    "/explain-question",
    response_model=AIExplanationResponse,
)
def explain_question_alias(
    request: dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Backward-compatible alias for /api/ai/explain.

    Frontend can use either:

        /api/ai/explain

    or:

        /api/ai/explain-question
    """

    return explain_question(
        request=request,
        db=db,
        current_user=current_user,
    )


# ============================================================
# GET /api/ai/health
# ============================================================

@router.get(
    "/health",
)
def ai_health():
    """
    Check the basic status of:

    - Gemini configuration
    - RAG availability
    - Verification Engine
    """

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        GeminiClient()

        gemini_configured = True

    except Exception:

        gemini_configured = False

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    try:

        RAGRetriever()

        rag_available = True

    except Exception:

        rag_available = False

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "service": "Gyan Sarthi AI",

        "status": "ok",

        "gemini_configured":
            gemini_configured,

        "rag_available":
            rag_available,

        "verification_engine":
            True,

        "timestamp":
            datetime.utcnow().isoformat(),
    }