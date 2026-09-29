import { apiRequest, getToken } from "./client";

export interface AIVerification {
  fact_score: number;
  formula_score: number;
  code_score: number;
  citation_score: number;
  hallucination_score: number;
  confidence_score: number;
  status: string;
  issues: string[];
  verified_claims: string[];
  unsupported_claims: string[];
}

export interface AIExplanationResponse {
  answer: string;
  verification: AIVerification;
  sources: string[];
  topic_id: number | null;
  question_id: number | null;
}

export interface AIExplainRequest {
  question: string;
  subject_code?: string;
  topic_id?: number;
  question_id?: number;
}

export async function explainQuestion(
  data: AIExplainRequest,
): Promise<AIExplanationResponse> {
  const token = getToken();

  if (!token) {
    throw new Error("Not authenticated. Please log in again.");
  }

  return apiRequest<AIExplanationResponse>(
    "/api/ai/explain",
    {
      method: "POST",
      token,
      body: JSON.stringify(data),
    },
  );
}

export async function getAIHealth() {
  return apiRequest<{
    service: string;
    status: string;
    gemini_configured: boolean;
    rag_available: boolean;
    verification_engine: boolean;
    timestamp: string;
  }>("/api/ai/health");
}