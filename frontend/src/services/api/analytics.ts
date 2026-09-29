import { apiRequest, getToken } from "./client";

/* =========================================================
   READINESS
========================================================= */

export type Readiness = {
  exam_id: number;

  readiness_score: number;

  mastery_score: number;

  exam_performance_score: number;

  accuracy_score: number;

  speed_score: number;

  consistency_score: number;

  readiness_level: string;
};

export type ReadinessTopic = {
  topic_id: number;

  topic: string;

  mastery_score: number;

  status: string;
};

export type ReadinessDashboard = {
  readiness: Readiness;

  topics: ReadinessTopic[];

  weak_topics: ReadinessTopic[];

  strong_topics: ReadinessTopic[];
};

/* =========================================================
   NEXT ACTION
========================================================= */

export type NextAction = {
  action: string;

  priority: number;

  topic_id: number | null;

  topic: string | null;

  reason: string;

  recommended_questions: number;

  estimated_minutes: number;
};

/* =========================================================
   ADAPTIVE PLAN
========================================================= */

export type AdaptiveTopicPlan = {
  topic_id: number;

  topic: string;

  mastery_score: number;

  forgetting_risk: number;

  mistake_score: number;

  recency_score: number;

  recent_performance: number;

  priority_score: number;

  action: string;

  recommended_questions: number;

  estimated_minutes: number;

  mistake_count: number;
};

export type AdaptivePlan = {
  exam_id: number;

  generated_at: string;

  topics: AdaptiveTopicPlan[];
};

/* =========================================================
   MISTAKES
========================================================= */

export type Mistake = {
  id: number;

  question_id: number;

  topic_id: number;

  mistake_type: string;

  explanation: string | null;

  created_at: string;
};

export type MistakeSummary = {
  total_mistakes: number;

  knowledge_gap: number;

  conceptual_error: number;

  time_pressure: number;

  careless_error: number;

  wrong_approach: number;

  most_common_mistake:
    | string
    | null;
};

/* =========================================================
   GET READINESS
========================================================= */

export async function getReadiness(
  examId: number,
): Promise<ReadinessDashboard> {
  return apiRequest<ReadinessDashboard>(
    `/api/analytics/readiness/${examId}`,
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET NEXT ACTION
========================================================= */

export async function getNextAction(): Promise<NextAction> {
  return apiRequest<NextAction>(
    "/api/analytics/next-action",
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET NEXT BEST ACTION
========================================================= */

export async function getNextBestAction(): Promise<NextAction> {
  return apiRequest<NextAction>(
    "/api/analytics/next-best-action",
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET ADAPTIVE PLAN
========================================================= */

export async function getAdaptivePlan(
  examId: number,
): Promise<AdaptivePlan> {
  return apiRequest<AdaptivePlan>(
    `/api/analytics/adaptive-plan/${examId}`,
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET TODAY PLAN
========================================================= */

export async function getTodayPlan(
  examId: number,
): Promise<AdaptivePlan> {
  return apiRequest<AdaptivePlan>(
    `/api/analytics/today-plan/${examId}`,
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET MISTAKE SUMMARY
========================================================= */

export async function getMistakeSummary(): Promise<MistakeSummary> {
  return apiRequest<MistakeSummary>(
    "/api/analytics/mistakes/summary",
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET MISTAKES
========================================================= */

export async function getMistakes(
  topicId?: number,
  limit = 50,
): Promise<Mistake[]> {
  const params = new URLSearchParams();

  if (topicId !== undefined) {
    params.set(
      "topic_id",
      String(topicId),
    );
  }

  params.set(
    "limit",
    String(limit),
  );

  return apiRequest<Mistake[]>(
    `/api/analytics/mistakes?${params.toString()}`,
    {
      method: "GET",

      token: getToken() || undefined,
    },
  );
}