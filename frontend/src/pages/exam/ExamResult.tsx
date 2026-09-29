import {
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  Clock3,
  RotateCcw,
  Target,
  XCircle,
} from "lucide-react";

import type {
  ExamResultResponse,
} from "../../services/api/exam";

type Props = {
  result: ExamResultResponse;
  onBack: () => void;
  onRetake: () => void;
};

function formatTime(
  seconds: number,
) {
  const minutes =
    Math.floor(seconds / 60);

  const remaining =
    seconds % 60;

  return `${minutes}m ${remaining}s`;
}

export default function ExamResult({
  result,
  onBack,
  onRetake,
}: Props) {
  return (
    <div className="mx-auto max-w-7xl space-y-8">

      {/* HEADER */}

      <section>

        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={16} />

          Back to Exams
        </button>

        <div className="mt-6">

          <p className="text-sm font-medium text-slate-500">
            Exam Result
          </p>

          <h1 className="mt-2 text-3xl font-bold text-slate-900">
            Exam Completed
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Here's your performance summary.
          </p>

        </div>

      </section>

      {/* SCORE */}

      <section className="grid gap-5 lg:grid-cols-[1fr_2fr]">

        <div className="rounded-2xl bg-slate-900 p-7 text-white">

          <p className="text-sm text-slate-300">
            Your Score
          </p>

          <p className="mt-3 text-5xl font-bold">
            {result.score}
          </p>

          <p className="mt-2 text-sm text-slate-400">
            out of {result.total_marks}
          </p>

          <div className="mt-7">

            <div className="mb-2 flex justify-between text-xs text-slate-400">
              <span>
                Accuracy
              </span>

              <span>
                {result.accuracy}%
              </span>
            </div>

            <div className="h-2 overflow-hidden rounded-full bg-white/10">

              <div
                className="h-full rounded-full bg-white"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      result.accuracy,
                    ),
                  )}%`,
                }}
              />

            </div>

          </div>

        </div>

        <div className="grid gap-4 sm:grid-cols-2">

          <StatCard
            icon={CheckCircle2}
            title="Correct"
            value={
              result.correct
            }
            description="Correct answers"
          />

          <StatCard
            icon={XCircle}
            title="Incorrect"
            value={
              result.incorrect
            }
            description="Incorrect answers"
          />

          <StatCard
            icon={Target}
            title="Attempted"
            value={
              result.attempted
            }
            description={`of ${result.total_questions} questions`}
          />

          <StatCard
            icon={Clock3}
            title="Time Used"
            value={formatTime(
              result.time_used_seconds,
            )}
            description={`of ${result.duration_minutes} minutes`}
          />

        </div>

      </section>

      {/* TOPIC PERFORMANCE */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-slate-100 p-3">
            <BarChart3
              size={20}
              className="text-slate-700"
            />
          </div>

          <div>

            <h2 className="font-bold text-slate-900">
              Topic Performance
            </h2>

            <p className="text-sm text-slate-500">
              Understand where you performed
              well and where more practice is
              needed.
            </p>

          </div>

        </div>

        {result.topic_performance.length ===
        0 ? (
          <div className="py-10 text-center text-sm text-slate-400">
            No topic performance data available.
          </div>
        ) : (
          <div className="mt-6 overflow-x-auto">

            <table className="w-full min-w-[650px]">

              <thead>

                <tr className="border-b border-slate-100 text-left">

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Topic
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Questions
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Attempted
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Correct
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Accuracy
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Marks
                  </th>

                </tr>

              </thead>

              <tbody>

                {result.topic_performance.map(
                  (topic) => (
                    <tr
                      key={
                        topic.topic_id
                      }
                      className="border-b border-slate-50 last:border-0"
                    >

                      <td className="py-4 font-semibold text-slate-800">
                        {topic.topic}
                      </td>

                      <td className="py-4 text-sm text-slate-600">
                        {
                          topic.total_questions
                        }
                      </td>

                      <td className="py-4 text-sm text-slate-600">
                        {
                          topic.attempted
                        }
                      </td>

                      <td className="py-4 text-sm font-semibold text-emerald-600">
                        {
                          topic.correct
                        }
                      </td>

                      <td className="py-4">

                        <div className="flex items-center gap-3">

                          <div className="h-2 w-20 overflow-hidden rounded-full bg-slate-100">

                            <div
                              className="h-full rounded-full bg-slate-900"
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    topic.accuracy,
                                  ),
                                )}%`,
                              }}
                            />

                          </div>

                          <span className="text-sm font-semibold text-slate-700">
                            {
                              topic.accuracy
                            }
                            %
                          </span>

                        </div>

                      </td>

                      <td className="py-4 text-sm font-semibold text-slate-700">
                        {
                          topic.marks
                        }
                      </td>

                    </tr>
                  ),
                )}

              </tbody>

            </table>

          </div>
        )}

      </section>

      {/* ACTIONS */}

      <section className="flex flex-col gap-3 sm:flex-row">

        <button
          type="button"
          onClick={onRetake}
          className="flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
        >
          <RotateCcw size={17} />

          Take Another Exam
        </button>

        <button
          type="button"
          onClick={onBack}
          className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
        >
          <ArrowLeft size={17} />

          Back to Exams
        </button>

      </section>

    </div>
  );
}

/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  icon: Icon,
  title,
  value,
  description,
}: {
  icon: typeof CheckCircle2;
  title: string;
  value: string | number;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold text-slate-900">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {description}
          </p>

        </div>

        <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
          <Icon size={19} />
        </div>

      </div>

    </div>
  );
}