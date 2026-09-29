import { apiRequest, getToken } from "./client";

export async function getDashboard(examId: number) {
  return apiRequest(`/api/analytics/dashboard/${examId}`, {
    token: getToken() || undefined,
  });
}

export async function getAdaptivePlan(examId: number) {
  return apiRequest(`/api/analytics/adaptive-plan/${examId}`, {
    token: getToken() || undefined,
  });
}

export async function getTodayPlan(examId: number) {
  return apiRequest(`/api/analytics/today-plan/${examId}`, {
    token: getToken() || undefined,
  });
}