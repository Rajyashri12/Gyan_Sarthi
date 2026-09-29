import { apiRequest, getToken } from "./client";

export type PracticeQuestion = {
  id: number;
  question_text: string;

  option_a: string | null;
  option_b: string | null;
  option_c: string | null;
  option_d: string | null;

  difficulty: string;
  question_type: string;

  is_pyq: boolean;
  exam_year: number | null;

  marks: number;
  negative_marks: number;
};

export type PracticeRequest = {
  subject_code?: string;
  topic?: string;
  difficulty?: string;
  limit?: number;
};

export type PracticeSubmitRequest = {
  question_id: number;
  selected_answer: string;
  time_taken_seconds: number;
  confidence?: number;
};

export type PracticeSubmitResponse = {
  question_id: number;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  marks_awarded: number;
  explanation: string | null;
};

export type AdaptivePracticeRequest = {
  exam_id: number;
  subject_code?: string;
  topic_id?: number;
  limit?: number;
};

export type AdaptiveQuestion = PracticeQuestion & {
  topic_id: number;
};

/* =========================================================
   NORMALIZE QUESTION
========================================================= */

function normalizeQuestion(
  question: any,
): PracticeQuestion {
  return {
    id: Number(question.id),

    question_text:
      question.question_text ?? "",

    option_a:
      question.option_a ??
      question.options?.A ??
      question.options?.a ??
      null,

    option_b:
      question.option_b ??
      question.options?.B ??
      question.options?.b ??
      null,

    option_c:
      question.option_c ??
      question.options?.C ??
      question.options?.c ??
      null,

    option_d:
      question.option_d ??
      question.options?.D ??
      question.options?.d ??
      null,

    difficulty:
      question.difficulty ?? "medium",

    question_type:
      question.question_type ?? "MCQ",

    is_pyq:
      Boolean(question.is_pyq),

    exam_year:
      question.exam_year ?? null,

    marks:
      Number(question.marks ?? 0),

    negative_marks:
      Number(question.negative_marks ?? 0),
  };
}

/* =========================================================
   GET PRACTICE QUESTIONS
========================================================= */

export async function getPracticeQuestions(
  payload: PracticeRequest,
): Promise<PracticeQuestion[]> {
  const response = await apiRequest<any>(
    "/api/practice/questions",
    {
      method: "POST",

      token: getToken() || undefined,

      body: JSON.stringify({
        subject_code:
          payload.subject_code ?? null,

        topic:
          payload.topic ?? null,

        difficulty:
          payload.difficulty ?? null,

        limit:
          payload.limit ?? 10,
      }),
    },
  );

  console.log(
    "RAW PRACTICE RESPONSE:",
    response,
  );

  /*
   * Your backend currently returns:
   *
   * [
   *   {
   *     id: 1,
   *     question_text: "...",
   *     option_a: "...",
   *     option_b: "...",
   *     option_c: "...",
   *     option_d: "..."
   *   }
   * ]
   */

  const questions = Array.isArray(response)
    ? response
    : response?.questions ?? [];

  const normalizedQuestions =
    questions.map(normalizeQuestion);

  console.log(
    "NORMALIZED QUESTIONS:",
    normalizedQuestions,
  );

  return normalizedQuestions;
}

/* =========================================================
   SUBMIT PRACTICE ANSWER
========================================================= */

export async function submitPracticeAnswer(
  payload: PracticeSubmitRequest,
): Promise<PracticeSubmitResponse> {
  return apiRequest<PracticeSubmitResponse>(
    "/api/practice/submit",
    {
      method: "POST",

      token: getToken() || undefined,

      body: JSON.stringify({
        question_id:
          payload.question_id,

        selected_answer:
          payload.selected_answer,

        time_taken_seconds:
          payload.time_taken_seconds ?? 0,

        confidence:
          payload.confidence ?? null,
      }),
    },
  );
}

/* =========================================================
   ADAPTIVE PRACTICE
========================================================= */

export async function getAdaptivePractice(
  payload: AdaptivePracticeRequest,
): Promise<AdaptiveQuestion[]> {
  const response = await apiRequest<any>(
    "/api/practice/adaptive",
    {
      method: "POST",
      token: getToken() || undefined,
      body: JSON.stringify({
        exam_id: payload.exam_id,
        subject_code: payload.subject_code ?? null,
        topic_id: payload.topic_id ?? null,
        limit: payload.limit ?? 10,
      }),
    },
  );

  const questions = Array.isArray(response)
    ? response
    : response?.questions ?? [];

  return questions.map(
    (question: any) => ({
      ...normalizeQuestion(question),
      topic_id: Number(question.topic_id),
    }),
  );
}