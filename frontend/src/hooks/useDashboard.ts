import { useEffect, useState } from "react";
import {
  getAdaptivePlan,
  getTodayPlan,
} from "../services/api/analytics";

const GATE_CSE_EXAM_ID = 1;

export type DashboardData = {
  adaptivePlan: any;
  todayPlan: any;
};

export function useDashboard() {
  const [data, setData] = useState<DashboardData>({
    adaptivePlan: null,
    todayPlan: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [adaptivePlan, todayPlan] =
          await Promise.all([
            getAdaptivePlan(GATE_CSE_EXAM_ID),
            getTodayPlan(GATE_CSE_EXAM_ID),
          ]);

        if (!mounted) return;

        setData({
          adaptivePlan,
          todayPlan,
        });
      } catch (err) {
        if (!mounted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load dashboard data.",
        );
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  return {
    ...data,
    loading,
    error,
  };
}