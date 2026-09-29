import { apiRequest, getToken } from "./client";

/* =========================================================
   TYPES
========================================================= */

export type ExamQuestion = {
  id: number;
  question_text: string;

  option_a: string | null;
  option_b: string | null;
  option_c: string | null;
  option_d: string | null;

  difficulty: string;
  question_type: string;

  marks: number;
  negative_marks: number;

  topic_id: number;
};

export type ExamStartRequest = {
  exam_id: number;
  total_questions: number;
  duration_minutes: number;
};

export type ExamStartResponse = {
  session_id: number;
  exam_id: number;
  total_questions: number;
  duration_minutes: number;
  started_at: string;
  questions: ExamQuestion[];
};

export type ExamAnswerRequest = {
  question_id: number;
  selected_answer: string | null;
  time_taken_seconds: number;
};

export type ExamAnswerResponse = {
  session_id: number;
  question_id: number;
  selected_answer: string | null;
  saved: boolean;
};

export type TopicPerformance = {
  topic_id: number;
  topic: string;
  total_questions: number;
  attempted: number;
  correct: number;
  accuracy: number;
  marks: number;
};

export type ExamResultResponse = {
  session_id: number;
  exam_id: number;

  total_questions: number;
  attempted: number;
  correct: number;
  incorrect: number;
  unanswered: number;

  total_marks: number;
  score: number;
  accuracy: number;

  duration_minutes: number;
  time_used_seconds: number;

  topic_performance: TopicPerformance[];
};

/* =========================================================
   START EXAM
========================================================= */

export async function startExam(
  request: ExamStartRequest,
): Promise<ExamStartResponse> {
  return apiRequest<ExamStartResponse>(
    "/api/exam/start",
    {
      method: "POST",
      token: getToken() || undefined,
      body: JSON.stringify(request),
    },
  );
}

/* =========================================================
   SAVE ANSWER
========================================================= */

export async function saveExamAnswer(
  sessionId: number,
  request: ExamAnswerRequest,
): Promise<ExamAnswerResponse> {
  return apiRequest<ExamAnswerResponse>(
    `/api/exam/${sessionId}/answer`,
    {
      method: "POST",
      token: getToken() || undefined,
      body: JSON.stringify(request),
    },
  );
}

/* =========================================================
   SUBMIT EXAM
========================================================= */

export async function submitExam(
  sessionId: number,
): Promise<ExamResultResponse> {
  return apiRequest<ExamResultResponse>(
    `/api/exam/${sessionId}/submit`,
    {
      method: "POST",
      token: getToken() || undefined,
    },
  );
}