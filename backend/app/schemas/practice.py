from pydantic import BaseModel, Field

class PracticeRequest(BaseModel):

    subject_code: str | None = None

    topic: str | None = None

    difficulty: str | None = None

    limit: int = 10


class PracticeQuestionResponse(BaseModel):

    id: int

    question_text: str

    option_a: str | None

    option_b: str | None

    option_c: str | None

    option_d: str | None

    difficulty: str

    question_type: str

    is_pyq: bool

    exam_year: int | None

    marks: float

    negative_marks: float


class PracticeSubmitRequest(BaseModel):

    question_id: int

    selected_answer: str

    time_taken_seconds: int = 0

    confidence: float | None = None


class PracticeSubmitResponse(BaseModel):

    question_id: int

    selected_answer: str

    correct_answer: str

    is_correct: bool

    marks_awarded: float

    explanation: str | None

class AdaptivePracticeRequest(BaseModel):
    exam_id: int
    subject_code: str | None = None
    topic_id: int | None = None
    limit: int = Field(default=10, ge=1, le=50)


class AdaptiveQuestionResponse(BaseModel):
    id: int
    question_text: str

    option_a: str | None
    option_b: str | None
    option_c: str | None
    option_d: str | None

    difficulty: str
    question_type: str

    is_pyq: bool
    exam_year: int | None

    marks: float
    negative_marks: float

    topic_id: int