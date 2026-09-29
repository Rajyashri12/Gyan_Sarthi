import { useState } from "react";
import {
  ArrowRight,
  BookOpen,
  Clock3,
  FileText,
  GraduationCap,
  ShieldCheck,
  Target,
} from "lucide-react";

import {
  startExam,
  type ExamStartResponse,
} from "../../services/api/exam";

type Props = {
  onExamStarted?: (
    exam: ExamStartResponse,
  ) => void;
};

export default function Exams({
  onExamStarted,
}: Props) {
  const [examId, setExamId] =
    useState(1);

  const [
    totalQuestions,
    setTotalQuestions,
  ] = useState(20);

  const [
    duration,
    setDuration,
  ] = useState(30);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  async function handleStartExam() {
    try {
      setLoading(true);
      setError("");

      const response =
        await startExam({
          exam_id: examId,
          total_questions:
            totalQuestions,
          duration_minutes:
            duration,
        });

      console.log(
        "EXAM STARTED:",
        response,
      );

      /*
       * Store locally as backup.
       */

      localStorage.setItem(
        "gyan_sarthi_exam",
        JSON.stringify(response),
      );

      if (onExamStarted) {
        onExamStarted(response);
      }

      /*
       * Navigate using browser
       * so this page also works
       * independently.
       */

      window.location.href =
        `/exam/session/${response.session_id}`;
    } catch (err) {
      console.error(
        "Exam start error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to start exam.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">

      {/* HEADER */}

      <section>

        <p className="text-sm font-medium text-slate-500">
          Gyan Sarthi
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          Exam Simulation
        </h1>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Simulate a real GATE-style exam,
          manage your time, and analyze your
          performance after submission.
        </p>

      </section>

      {/* ERROR */}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* MAIN GRID */}

      <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">

        {/* CONFIGURATION */}

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-slate-100 p-3">
              <GraduationCap
                size={22}
                className="text-slate-700"
              />
            </div>

            <div>

              <h2 className="font-bold text-slate-900">
                Configure Exam
              </h2>

              <p className="text-sm text-slate-500">
                Choose your exam parameters.
              </p>

            </div>

          </div>

          <div className="mt-8 space-y-6">

            {/* EXAM */}

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Exam
              </label>

              <select
                value={examId}
                onChange={(e) =>
                  setExamId(
                    Number(
                      e.target.value,
                    ),
                  )
                }
                className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-slate-400"
              >
                <option value={1}>
                  GATE CSE
                </option>
              </select>

            </div>

            {/* QUESTIONS */}

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Number of Questions
              </label>

              <div className="mt-2 grid grid-cols-3 gap-3">

                {[10, 20, 30].map(
                  (value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() =>
                        setTotalQuestions(
                          value,
                        )
                      }
                      className={[
                        "rounded-xl border px-4 py-3 text-sm font-semibold transition",

                        totalQuestions ===
                        value
                          ? "border-slate-900 bg-slate-900 text-white"
                          : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50",
                      ].join(" ")}
                    >
                      {value}
                    </button>
                  ),
                )}

              </div>

            </div>

            {/* DURATION */}

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Duration
              </label>

              <div className="mt-2 grid grid-cols-3 gap-3">

                {[15, 30, 60].map(
                  (value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() =>
                        setDuration(
                          value,
                        )
                      }
                      className={[
                        "rounded-xl border px-4 py-3 text-sm font-semibold transition",

                        duration === value
                          ? "border-slate-900 bg-slate-900 text-white"
                          : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50",
                      ].join(" ")}
                    >
                      {value} min
                    </button>
                  ),
                )}

              </div>

            </div>

            {/* START */}

            <button
              type="button"
              onClick={
                handleStartExam
              }
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />

                  Starting Exam...
                </>
              ) : (
                <>
                  Start Exam

                  <ArrowRight
                    size={17}
                  />
                </>
              )}
            </button>

          </div>

        </section>

        {/* INFO */}

        <section className="space-y-4">

          <InfoCard
            icon={Clock3}
            title="Timed Simulation"
            description="Practice under a fixed time limit to improve speed and time management."
          />

          <InfoCard
            icon={Target}
            title="Performance Analysis"
            description="After submission, view score, accuracy, attempted questions and topic performance."
          />

          <InfoCard
            icon={ShieldCheck}
            title="Exam Session"
            description="Your answers are saved against an authenticated exam session."
          />

          <InfoCard
            icon={BookOpen}
            title="Topic Intelligence"
            description="See which topics need more practice after your exam."
          />

        </section>

      </div>

      {/* EXAM STRUCTURE */}

      <section className="rounded-2xl bg-slate-900 p-6 text-white">

        <div className="flex items-start gap-4">

          <div className="rounded-xl bg-white/10 p-3">
            <FileText size={22} />
          </div>

          <div>

            <h2 className="font-bold">
              Exam Simulation Workflow
            </h2>

            <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-slate-300">

              <span>
                Configure
              </span>

              <span>→</span>

              <span>
                Start
              </span>

              <span>→</span>

              <span>
                Attempt
              </span>

              <span>→</span>

              <span>
                Review
              </span>

              <span>→</span>

              <span>
                Submit
              </span>

              <span>→</span>

              <span>
                Analyze
              </span>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

/* =========================================================
   INFO CARD
========================================================= */

function InfoCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Clock3;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex items-start gap-4">

        <div className="rounded-xl bg-slate-100 p-3">
          <Icon
            size={20}
            className="text-slate-700"
          />
        </div>

        <div>

          <h3 className="font-semibold text-slate-900">
            {title}
          </h3>

          <p className="mt-1 text-sm leading-6 text-slate-500">
            {description}
          </p>

        </div>

      </div>

    </div>
  );
}