from pydantic import BaseModel, Field


class AIExplainRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="Student question"
    )

    subject_code: str | None = None

    topic: str | None = None


class AISource(BaseModel):
    content: str
    subject: str
    topic: str
    source_file: str


class AIVerification(BaseModel):
    status: str
    confidence_score: float


class AIExplainResponse(BaseModel):
    question: str
    answer: str
    verification: AIVerification
    sources: list[AISource]

class VerificationResult(BaseModel):
    fact_score: float = Field(ge=0, le=1)
    formula_score: float = Field(ge=0, le=1)
    code_score: float = Field(ge=0, le=1)
    citation_score: float = Field(ge=0, le=1)
    hallucination_score: float = Field(ge=0, le=1)

    confidence_score: float = Field(ge=0, le=1)

    status: str

    issues: list[str] = []
    verified_claims: list[str] = []
    unsupported_claims: list[str] = []


class AIExplanationResponse(BaseModel):
    answer: str

    verification: VerificationResult

    sources: list[str] = []

    topic_id: int | None = None
    question_id: int | None = None