import { apiRequest, getToken } from "./client";

/* =========================================================
   TYPES
========================================================= */

export type Revision = {
  revision_id: number;

  topic_id: number;

  topic: string;

  scheduled_at: string;

  mastery_score: number;

  forgetting_risk: number;

  mistake_count: number;

  priority_score: number;

  status: string;
};

export type RevisionCompleteRequest = {
  recall_score: number;
};

export type RevisionCompleteResponse = {
  revision_id: number;

  topic_id: number;

  recall_score: number;

  completed_at: string;

  next_revision_id: number | null;

  next_revision_at: string | null;
};

/* =========================================================
   GET DUE REVISIONS
========================================================= */

export async function getDueRevisions(): Promise<Revision[]> {
  return apiRequest<Revision[]>(
    "/api/revision/due",
    {
      method: "GET",
      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET REVISION DASHBOARD
========================================================= */

export async function getRevisionDashboard(): Promise<Revision[]> {
  return apiRequest<Revision[]>(
    "/api/revision/dashboard",
    {
      method: "GET",
      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   GET UPCOMING REVISIONS
========================================================= */

export async function getUpcomingRevisions(
  days = 7,
): Promise<Revision[]> {
  const safeDays = Math.min(
    30,
    Math.max(1, days),
  );

  return apiRequest<Revision[]>(
    `/api/revision/upcoming?days=${safeDays}`,
    {
      method: "GET",
      token: getToken() || undefined,
    },
  );
}

/* =========================================================
   COMPLETE REVISION
========================================================= */

export async function completeRevision(
  revisionId: number,
  recallScore: number,
): Promise<RevisionCompleteResponse> {
  return apiRequest<RevisionCompleteResponse>(
    `/api/revision/${revisionId}/complete`,
    {
      method: "POST",

      token: getToken() || undefined,

      body: JSON.stringify({
        recall_score: recallScore,
      }),
    },
  );
}