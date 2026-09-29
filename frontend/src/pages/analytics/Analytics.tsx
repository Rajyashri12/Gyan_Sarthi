import { useEffect, useMemo, useState } from "react";

import {
  AlertTriangle,
  ArrowRight,
  Brain,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Target,
  TrendingUp,
  Zap,
} from "lucide-react";

import {
  getAdaptivePlan,
  getMistakeSummary,
  getNextAction,
  getNextBestAction,
  getReadiness,
  getTodayPlan,
  type AdaptivePlan,
  type MistakeSummary,
  type NextAction,
  type ReadinessDashboard,
} from "../../services/api/analytics";

/* =========================================================
   CONFIG
========================================================= */

const GATE_EXAM_ID = 1;

/* =========================================================
   HELPERS
========================================================= */

function formatAction(
  action: string | undefined,
) {
  if (!action) {
    return "—";
  }

  return action
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

function getMasteryBarClass(
  score: number,
) {
  if (score < 40) {
    return "bg-red-500";
  }

  if (score < 70) {
    return "bg-amber-500";
  }

  if (score < 85) {
    return "bg-blue-500";
  }

  return "bg-emerald-500";
}

function getStatusClass(
  status: string,
) {
  switch (status) {
    case "WEAK":
      return "bg-red-50 text-red-700";

    case "DEVELOPING":
      return "bg-amber-50 text-amber-700";

    case "STRONG":
      return "bg-blue-50 text-blue-700";

    case "MASTERED":
      return "bg-emerald-50 text-emerald-700";

    default:
      return "bg-slate-100 text-slate-600";
  }
}

/* =========================================================
   ANALYTICS PAGE
========================================================= */

export default function Analytics() {
  const [
    readinessData,
    setReadinessData,
  ] =
    useState<ReadinessDashboard | null>(
      null,
    );

  const [
    nextAction,
    setNextAction,
  ] = useState<NextAction | null>(
    null,
  );

  const [
    nextBestAction,
    setNextBestAction,
  ] = useState<NextAction | null>(
    null,
  );

  const [
    adaptivePlan,
    setAdaptivePlan,
  ] = useState<AdaptivePlan | null>(
    null,
  );

  const [
    todayPlan,
    setTodayPlan,
  ] = useState<AdaptivePlan | null>(
    null,
  );

  const [
    mistakeSummary,
    setMistakeSummary,
  ] =
    useState<MistakeSummary | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  /* =======================================================
     LOAD ANALYTICS
  ======================================================== */

  async function loadAnalytics() {
    try {
      setLoading(true);

      setError("");

      const [
        readiness,
        action,
        bestAction,
        adaptive,
        today,
        mistakes,
      ] = await Promise.all([
        getReadiness(
          GATE_EXAM_ID,
        ),

        getNextAction(),

        getNextBestAction(),

        getAdaptivePlan(
          GATE_EXAM_ID,
        ),

        getTodayPlan(
          GATE_EXAM_ID,
        ),

        getMistakeSummary(),
      ]);

      console.log(
        "READINESS:",
        readiness,
      );

      console.log(
        "NEXT ACTION:",
        action,
      );

      console.log(
        "NEXT BEST ACTION:",
        bestAction,
      );

      console.log(
        "ADAPTIVE PLAN:",
        adaptive,
      );

      console.log(
        "TODAY PLAN:",
        today,
      );

      console.log(
        "MISTAKE SUMMARY:",
        mistakes,
      );

      setReadinessData(
        readiness,
      );

      setNextAction(action);

      setNextBestAction(
        bestAction,
      );

      setAdaptivePlan(
        adaptive,
      );

      setTodayPlan(today);

      setMistakeSummary(
        mistakes,
      );
    } catch (err) {
      console.error(
        "Analytics error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load analytics.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, []);

  /* =======================================================
     DERIVED DATA
  ======================================================== */

  const readiness =
    readinessData?.readiness;

  const topics =
    readinessData?.topics ?? [];

  const weakTopics =
    readinessData?.weak_topics ?? [];

  const strongTopics =
    readinessData?.strong_topics ?? [];

  const displayedPlan =
    todayPlan?.topics ??
    adaptivePlan?.topics ??
    [];

  const averageMastery =
    useMemo(() => {
      if (!topics.length) {
        return 0;
      }

      return (
        topics.reduce(
          (total, topic) =>
            total +
            topic.mastery_score,
          0,
        ) / topics.length
      );
    }, [topics]);

  /* =======================================================
     LOADING
  ======================================================== */

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />

          <p className="mt-4 text-sm font-medium text-slate-600">
            Loading your analytics...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Gyan Sarthi is analyzing your
            preparation data.
          </p>

        </div>
      </div>
    );
  }

  /* =======================================================
     ERROR
  ======================================================== */

  if (error) {
    return (
      <div className="mx-auto max-w-3xl py-16">

        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">

          <div className="flex items-start gap-4">

            <AlertTriangle
              className="mt-0.5 shrink-0 text-red-600"
              size={24}
            />

            <div>

              <h2 className="font-semibold text-red-800">
                Unable to load analytics
              </h2>

              <p className="mt-2 text-sm leading-6 text-red-700">
                {error}
              </p>

              <button
                type="button"
                onClick={
                  loadAnalytics
                }
                className="mt-4 flex items-center gap-2 rounded-xl bg-red-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-800"
              >
                <RefreshCw
                  size={16}
                />
                Try again
              </button>

            </div>

          </div>

        </div>

      </div>
    );
  }

  /* =======================================================
     PAGE
  ======================================================== */

  return (
    <div className="mx-auto max-w-7xl space-y-8">

      {/* =================================================
          HEADER
      ================================================== */}

      <section>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

          <div>

            <p className="text-sm font-medium text-slate-500">
              Gyan Sarthi
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              Analytics
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Understand your preparation,
              identify weak areas, and see
              what Gyan Sarthi recommends
              next.
            </p>

          </div>

          <button
            type="button"
            onClick={
              loadAnalytics
            }
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
          >
            <RefreshCw
              size={16}
            />
            Refresh
          </button>

        </div>
      </section>

      {/* =================================================
          TOP METRICS
      ================================================== */}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        {/* Readiness */}

        <MetricCard
          title="Exam Readiness"
          value={
            readiness
              ? `${readiness.readiness_score.toFixed(
                  0,
                )}%`
              : "—"
          }
          description={
            readiness
              ?.readiness_level
              ? formatAction(
                  readiness.readiness_level,
                )
              : "Not assessed"
          }
          icon={Target}
        />

        {/* Mastery */}

        <MetricCard
          title="Average Mastery"
          value={`${averageMastery.toFixed(
            0,
          )}%`}
          description="Across assessed topics"
          icon={Brain}
        />

        {/* Accuracy */}

        <MetricCard
          title="Accuracy"
          value={
            readiness
              ? `${readiness.accuracy_score.toFixed(
                  0,
                )}%`
              : "—"
          }
          description="Practice attempts"
          icon={CheckCircle2}
        />

        {/* Speed */}

        <MetricCard
          title="Speed"
          value={
            readiness
              ? `${readiness.speed_score.toFixed(
                  0,
                )}%`
              : "—"
          }
          description="Based on solving time"
          icon={Clock3}
        />

      </section>

      {/* =================================================
          READINESS BREAKDOWN
      ================================================== */}

      {readiness && (
        <section className="grid gap-6 lg:grid-cols-3">

          {/* Main readiness */}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-sm font-medium text-slate-500">
                  GATE CSE Readiness
                </p>

                <h2 className="mt-2 text-4xl font-bold text-slate-900">
                  {readiness.readiness_score.toFixed(
                    1,
                  )}
                  %
                </h2>

              </div>

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100">
                <TrendingUp
                  size={23}
                  className="text-slate-700"
                />
              </div>

            </div>

            <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">

              <div
                className="h-full rounded-full bg-slate-900 transition-all"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      readiness.readiness_score,
                    ),
                  )}%`,
                }}
              />

            </div>

            <div className="mt-4 flex items-center justify-between">

              <span className="text-xs text-slate-400">
                Current level
              </span>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                {formatAction(
                  readiness.readiness_level,
                )}
              </span>

            </div>

          </div>

          {/* Score breakdown */}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">

            <h2 className="font-bold text-slate-900">
              Readiness Breakdown
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Current components contributing
              to your readiness score.
            </p>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">

              <ScoreBar
                label="Mastery"
                value={
                  readiness.mastery_score
                }
              />

              <ScoreBar
                label="Exam Performance"
                value={
                  readiness.exam_performance_score
                }
              />

              <ScoreBar
                label="Accuracy"
                value={
                  readiness.accuracy_score
                }
              />

              <ScoreBar
                label="Speed"
                value={
                  readiness.speed_score
                }
              />

              <ScoreBar
                label="Consistency"
                value={
                  readiness.consistency_score
                }
              />

            </div>

          </div>

        </section>
      )}

      {/* =================================================
          NEXT ACTION
      ================================================== */}

      <section className="grid gap-6 lg:grid-cols-2">

        <ActionCard
          title="Next Action"
          action={nextAction}
          icon={Zap}
        />

        <ActionCard
          title="Next Best Action"
          action={
            nextBestAction
          }
          icon={Target}
        />

      </section>

      {/* =================================================
          TOPIC MASTERY
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between">

          <div>

            <h2 className="text-lg font-bold text-slate-900">
              Topic Mastery
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Your current mastery by assessed
              topic.
            </p>

          </div>

          <Brain
            size={21}
            className="text-slate-400"
          />

        </div>

        {topics.length === 0 ? (
          <EmptyState
            text="Complete some practice questions to build topic mastery."
          />
        ) : (
          <div className="mt-6 space-y-5">

            {topics.map(
              (topic) => (
                <div
                  key={
                    topic.topic_id
                  }
                >

                  <div className="mb-2 flex items-center justify-between gap-4">

                    <div className="flex min-w-0 items-center gap-3">

                      <p className="truncate text-sm font-semibold text-slate-800">
                        {topic.topic}
                      </p>

                      <span
                        className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase ${getStatusClass(
                          topic.status,
                        )}`}
                      >
                        {
                          topic.status
                        }
                      </span>

                    </div>

                    <span className="shrink-0 text-sm font-bold text-slate-700">
                      {topic.mastery_score.toFixed(
                        0,
                      )}
                      %
                    </span>

                  </div>

                  <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">

                    <div
                      className={`h-full rounded-full transition-all ${getMasteryBarClass(
                        topic.mastery_score,
                      )}`}
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            topic.mastery_score,
                          ),
                        )}%`,
                      }}
                    />

                  </div>

                </div>
              ),
            )}

          </div>
        )}

      </section>

      {/* =================================================
          WEAK + STRONG TOPICS
      ================================================== */}

      <section className="grid gap-6 lg:grid-cols-2">

        {/* Weak */}

        <TopicListCard
          title="Weak Topics"
          description="Topics that currently need more attention."
          topics={weakTopics}
          icon={AlertTriangle}
          emptyText="No weak topics have been identified."
        />

        {/* Strong */}

        <TopicListCard
          title="Strong Topics"
          description="Topics where your current mastery is strong."
          topics={strongTopics}
          icon={CheckCircle2}
          emptyText="Complete more practice to identify strong topics."
        />

      </section>

      {/* =================================================
          MISTAKE INTELLIGENCE
      ================================================== */}

      {mistakeSummary && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="flex items-start justify-between gap-4">

            <div>

              <h2 className="text-lg font-bold text-slate-900">
                Mistake Intelligence
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Understand the types of mistakes
                appearing in your practice.
              </p>

            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
              <AlertTriangle
                size={20}
                className="text-slate-700"
              />
            </div>

          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">

            <MistakeCard
              label="Knowledge Gap"
              value={
                mistakeSummary.knowledge_gap
              }
            />

            <MistakeCard
              label="Conceptual Error"
              value={
                mistakeSummary.conceptual_error
              }
            />

            <MistakeCard
              label="Time Pressure"
              value={
                mistakeSummary.time_pressure
              }
            />

            <MistakeCard
              label="Careless Error"
              value={
                mistakeSummary.careless_error
              }
            />

            <MistakeCard
              label="Wrong Approach"
              value={
                mistakeSummary.wrong_approach
              }
            />

          </div>

          <div className="mt-5 rounded-xl bg-slate-50 p-4">

            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

              <span className="text-sm text-slate-500">
                Total mistakes
              </span>

              <span className="text-xl font-bold text-slate-900">
                {
                  mistakeSummary.total_mistakes
                }
              </span>

            </div>

            {mistakeSummary.most_common_mistake && (
              <div className="mt-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">

                <span className="text-sm text-slate-500">
                  Most common mistake
                </span>

                <span className="rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 ring-1 ring-slate-200">
                  {formatAction(
                    mistakeSummary.most_common_mistake,
                  )}
                </span>

              </div>
            )}

          </div>

        </section>
      )}

      {/* =================================================
          TODAY'S PLAN
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between gap-4">

          <div>

            <h2 className="text-lg font-bold text-slate-900">
              Today's Adaptive Plan
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Topics prioritized using your
              current learning signals.
            </p>

          </div>

          <Clock3
            size={21}
            className="text-slate-400"
          />

        </div>

        {displayedPlan.length === 0 ? (
          <EmptyState
            text="Your adaptive plan will appear after Gyan Sarthi has enough learning activity."
          />
        ) : (
          <div className="mt-6 overflow-x-auto">

            <table className="w-full min-w-[700px]">

              <thead>

                <tr className="border-b border-slate-100 text-left">

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Topic
                  </th>

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Mastery
                  </th>

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Action
                  </th>

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Questions
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Priority
                  </th>

                </tr>

              </thead>

              <tbody>

                {displayedPlan.map(
                  (item) => (
                    <tr
                      key={
                        item.topic_id
                      }
                      className="border-b border-slate-50 last:border-0"
                    >

                      <td className="py-4 pr-4">

                        <p className="font-semibold text-slate-800">
                          {item.topic}
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          {item.estimated_minutes} min
                          estimated
                        </p>

                      </td>

                      <td className="py-4 pr-4">

                        <span className="text-sm font-semibold text-slate-700">
                          {item.mastery_score.toFixed(
                            0,
                          )}
                          %
                        </span>

                      </td>

                      <td className="py-4 pr-4">

                        <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700">
                          {formatAction(
                            item.action,
                          )}
                        </span>

                      </td>

                      <td className="py-4 pr-4">

                        <span className="text-sm font-semibold text-slate-700">
                          {
                            item.recommended_questions
                          }
                        </span>

                      </td>

                      <td className="py-4">

                        <div className="flex items-center gap-3">

                          <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">

                            <div
                              className="h-full rounded-full bg-slate-900"
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    item.priority_score,
                                  ),
                                )}%`,
                              }}
                            />

                          </div>

                          <span className="text-xs font-semibold text-slate-600">
                            {item.priority_score.toFixed(
                              0,
                            )}
                          </span>

                        </div>

                      </td>

                    </tr>
                  ),
                )}

              </tbody>

            </table>

          </div>
        )}

      </section>

      {/* =================================================
          ADAPTIVE DETAILS
      ================================================== */}

      {adaptivePlan &&
        adaptivePlan.topics.length >
          0 && (
          <section className="rounded-2xl bg-slate-900 p-6 text-white">

            <div className="flex items-start gap-4">

              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/10">
                <Zap size={21} />
              </div>

              <div>

                <h2 className="font-bold">
                  Adaptive Intelligence
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  Gyan Sarthi considers mastery,
                  forgetting risk, mistakes,
                  recency and recent performance
                  when prioritizing topics.
                </p>

              </div>

            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

              <DarkMetric
                label="Topics analyzed"
                value={
                  adaptivePlan
                    .topics.length
                }
              />

              <DarkMetric
                label="Highest priority"
                value={
                  adaptivePlan
                    .topics[0]
                    ?.topic ?? "—"
                }
              />

              <DarkMetric
                label="Recommended questions"
                value={adaptivePlan.topics.reduce(
                  (
                    total,
                    topic,
                  ) =>
                    total +
                    topic.recommended_questions,
                  0,
                )}
              />

              <DarkMetric
                label="Estimated time"
                value={`${adaptivePlan.topics.reduce(
                  (
                    total,
                    topic,
                  ) =>
                    total +
                    topic.estimated_minutes,
                  0,
                )} min`}
              />

            </div>

          </section>
        )}

    </div>
  );
}

/* =========================================================
   METRIC CARD
========================================================= */

function MetricCard({
  title,
  value,
  description,
  icon: Icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: typeof Target;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-900">
            {value}
          </p>

        </div>

        <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
          <Icon size={20} />
        </div>

      </div>

      <p className="mt-4 text-xs text-slate-400">
        {description}
      </p>

    </div>
  );
}

/* =========================================================
   SCORE BAR
========================================================= */

function ScoreBar({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div>

      <div className="mb-2 flex items-center justify-between">

        <span className="text-xs font-medium text-slate-500">
          {label}
        </span>

        <span className="text-xs font-bold text-slate-700">
          {value.toFixed(0)}%
        </span>

      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-100">

        <div
          className="h-full rounded-full bg-slate-900"
          style={{
            width: `${Math.min(
              100,
              Math.max(
                0,
                value,
              ),
            )}%`,
          }}
        />

      </div>

    </div>
  );
}

/* =========================================================
   ACTION CARD
========================================================= */

function ActionCard({
  title,
  action,
  icon: Icon,
}: {
  title: string;
  action: NextAction | null;
  icon: typeof Target;
}) {
  if (!action) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <h2 className="font-bold text-slate-900">
          {title}
        </h2>

        <p className="mt-4 text-sm text-slate-500">
          No recommendation is available
          yet.
        </p>

      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <h2 className="mt-2 text-xl font-bold text-slate-900">
            {formatAction(
              action.action,
            )}
          </h2>

        </div>

        <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
          <Icon size={20} />
        </div>

      </div>

      {action.topic && (
        <p className="mt-4 text-sm font-semibold text-slate-700">
          Focus: {action.topic}
        </p>
      )}

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {action.reason}
      </p>

      <div className="mt-5 flex flex-wrap gap-2">

        <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700">
          {action.recommended_questions} questions
        </span>

        <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700">
          {action.estimated_minutes} min
        </span>

        <span className="rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white">
          Priority {action.priority.toFixed(0)}
        </span>

      </div>

      <button
        type="button"
        className="mt-5 flex items-center gap-2 text-sm font-semibold text-slate-700 hover:text-slate-900"
      >
        View recommendation
        <ArrowRight size={16} />
      </button>

    </div>
  );
}

/* =========================================================
   TOPIC LIST CARD
========================================================= */

function TopicListCard({
  title,
  description,
  topics,
  icon: Icon,
  emptyText,
}: {
  title: string;
  description: string;
  topics: ReadinessDashboard["topics"];
  icon: typeof Target;
  emptyText: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <h2 className="text-lg font-bold text-slate-900">
            {title}
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            {description}
          </p>

        </div>

        <Icon
          size={21}
          className="text-slate-400"
        />

      </div>

      {topics.length === 0 ? (
        <EmptyState
          text={emptyText}
          compact
        />
      ) : (
        <div className="mt-5 space-y-3">

          {topics.map(
            (topic) => (
              <div
                key={
                  topic.topic_id
                }
                className="flex items-center justify-between rounded-xl bg-slate-50 p-4"
              >

                <div className="min-w-0">

                  <p className="truncate text-sm font-semibold text-slate-800">
                    {topic.topic}
                  </p>

                  <span
                    className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${getStatusClass(
                      topic.status,
                    )}`}
                  >
                    {topic.status}
                  </span>

                </div>

                <span className="ml-4 text-sm font-bold text-slate-700">
                  {topic.mastery_score.toFixed(
                    0,
                  )}
                  %
                </span>

              </div>
            ),
          )}

        </div>
      )}

    </div>
  );
}

/* =========================================================
   MISTAKE CARD
========================================================= */

function MistakeCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">

      <p className="text-xs font-medium leading-5 text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
      </p>

    </div>
  );
}

/* =========================================================
   DARK METRIC
========================================================= */

function DarkMetric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl bg-white/10 p-4">

      <p className="text-xs text-slate-400">
        {label}
      </p>

      <p className="mt-2 truncate text-lg font-bold text-white">
        {value}
      </p>

    </div>
  );
}

/* =========================================================
   EMPTY STATE
========================================================= */

function EmptyState({
  text,
  compact = false,
}: {
  text: string;
  compact?: boolean;
}) {
  return (
    <div
      className={`text-center ${
        compact
          ? "py-8"
          : "py-12"
      }`}
    >
      <Brain
        size={compact ? 22 : 28}
        className="mx-auto text-slate-300"
      />

      <p className="mx-auto mt-3 max-w-md text-xs leading-5 text-slate-400">
        {text}
      </p>
    </div>
  );
}