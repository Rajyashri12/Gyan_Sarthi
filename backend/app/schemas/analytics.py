from datetime import datetime

from pydantic import BaseModel, Field


class ReadinessResponse(BaseModel):
    exam_id: int

    readiness_score: float

    mastery_score: float
    exam_performance_score: float
    accuracy_score: float
    speed_score: float
    consistency_score: float

    readiness_level: str


class ReadinessTopic(BaseModel):
    topic_id: int
    topic: str
    mastery_score: float
    status: str


class ReadinessDashboardResponse(BaseModel):
    readiness: ReadinessResponse
    topics: list[ReadinessTopic]
    weak_topics: list[ReadinessTopic]
    strong_topics: list[ReadinessTopic]

class NextActionResponse(BaseModel):
    action: str
    priority: float

    topic_id: int | None = None
    topic: str | None = None

    reason: str

    recommended_questions: int
    estimated_minutes: int

class AdaptiveTopicPlan(BaseModel):
    topic_id: int
    topic: str

    mastery_score: float
    forgetting_risk: float

    mistake_score: float
    recency_score: float
    recent_performance: float

    priority_score: float

    action: str

    recommended_questions: int
    estimated_minutes: int

    mistake_count: int


class AdaptivePlanResponse(BaseModel):
    exam_id: int
    generated_at: str
    topics: list[AdaptiveTopicPlan]


class DiagnosticStartRequest(BaseModel):
    exam_id: int
    questions_per_subject: int = 5


class DiagnosticQuestionResponse(BaseModel):
    id: int
    question_text: str

    option_a: str | None
    option_b: str | None
    option_c: str | None
    option_d: str | None

    difficulty: str
    question_type: str

    marks: float
    negative_marks: float

    subject_code: str
    topic_id: int


class DiagnosticStartResponse(BaseModel):
    session_id: int
    exam_id: int

    total_questions: int
    started_at: datetime

    questions: list[DiagnosticQuestionResponse]


class DiagnosticAnswerRequest(BaseModel):
    question_id: int
    selected_answer: str | None = None
    time_taken_seconds: int = Field(
        default=0,
        ge=0,
    )


class DiagnosticAnswerResponse(BaseModel):
    session_id: int
    question_id: int
    selected_answer: str | None
    saved: bool


class DiagnosticTopicResult(BaseModel):
    topic_id: int
    topic: str
    total_questions: int
    attempted: int
    correct: int
    accuracy: float


class DiagnosticResultResponse(BaseModel):
    session_id: int
    exam_id: int

    total_questions: int
    attempted: int
    correct: int
    incorrect: int
    unanswered: int

    score: float
    accuracy: float

    topic_results: list[DiagnosticTopicResult]

class DiagnosticMasteryResult(BaseModel):
    topic_id: int
    mastery_score: float
    accuracy: float
    attempts_count: int
    average_time_seconds: float


class DiagnosticResultResponse(BaseModel):
    session_id: int
    exam_id: int
    total_questions: int
    attempted: int
    correct: int
    incorrect: int
    unanswered: int
    score: float
    accuracy: float
    topic_results: list[DiagnosticTopicResult]
    initial_mastery: list[DiagnosticMasteryResult]

class MistakeResponse(BaseModel):
    id: int
    question_id: int
    topic_id: int
    mistake_type: str
    explanation: str | None
    created_at: datetime


class MistakeSummaryResponse(BaseModel):
    total_mistakes: int
    knowledge_gap: int
    conceptual_error: int
    time_pressure: int
    careless_error: int
    wrong_approach: int
    most_common_mistake: str | None


class TopicMistakeResponse(BaseModel):
    topic_id: int
    mistake_count: int

class RevisionResponse(BaseModel):
    revision_id: int
    topic_id: int
    topic: str
    scheduled_at: datetime

    mastery_score: float
    forgetting_risk: float

    mistake_count: int
    priority_score: float

    status: str


class RevisionCompleteRequest(BaseModel):
    recall_score: float = Field(
        ge=0,
        le=100
    )


class RevisionCompleteResponse(BaseModel):
    revision_id: int
    topic_id: int
    recall_score: float

    completed_at: datetime

    next_revision_id: int | None
    next_revision_at: datetime | None