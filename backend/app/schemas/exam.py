from datetime import datetime

from pydantic import BaseModel, Field


class ExamStartRequest(BaseModel):
    exam_id: int
    total_questions: int = Field(default=20, ge=1, le=100)
    duration_minutes: int = Field(default=30, ge=1, le=180)


class ExamQuestionResponse(BaseModel):
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

    topic_id: int


class ExamStartResponse(BaseModel):
    session_id: int
    exam_id: int
    total_questions: int
    duration_minutes: int
    started_at: datetime
    questions: list[ExamQuestionResponse]


class ExamAnswerRequest(BaseModel):
    question_id: int
    selected_answer: str | None = None
    time_taken_seconds: int = Field(default=0, ge=0)


class ExamAnswerResponse(BaseModel):
    session_id: int
    question_id: int
    selected_answer: str | None
    saved: bool


class TopicPerformance(BaseModel):
    topic_id: int
    topic: str
    total_questions: int
    attempted: int
    correct: int
    accuracy: float
    marks: float


class ExamResultResponse(BaseModel):
    session_id: int
    exam_id: int

    total_questions: int
    attempted: int
    correct: int
    incorrect: int
    unanswered: int

    total_marks: float
    score: float
    accuracy: float

    duration_minutes: int
    time_used_seconds: int

    topic_performance: list[TopicPerformance]