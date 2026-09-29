import {
  ArrowRight,
  Brain,
  CheckCircle2,
  Clock3,
  Flame,
  Target,
  TrendingUp,
  BookOpen,
} from "lucide-react";

import { useDashboard } from "../../hooks/useDashboard";

const subjects = [
  {
    name: "General Aptitude",
    code: "GA",
  },
  {
    name: "Database Management Systems",
    code: "DBMS",
  },
  {
    name: "Operating Systems",
    code: "OS",
  },
  {
    name: "Computer Networks",
    code: "CN",
  },
];

function LoadingCard() {
  return (
    <div className="h-36 animate-pulse rounded-2xl border border-slate-200 bg-white p-5">
      <div className="h-4 w-28 rounded bg-slate-200" />
      <div className="mt-4 h-8 w-20 rounded bg-slate-200" />
      <div className="mt-4 h-3 w-36 rounded bg-slate-100" />
    </div>
  );
}

export default function Dashboard() {
  const {
    adaptivePlan,
    todayPlan,
    loading,
    error,
  } = useDashboard();

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl space-y-8">

        <section>
          <p className="mb-2 text-sm font-medium text-slate-500">
            Gyan Sarthi
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Loading your dashboard...
          </h1>

          <p className="mt-2 text-slate-500">
            Analysing your preparation data.
          </p>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8">

      {/* =====================================================
          HEADER
      ====================================================== */}
      <section>
        <p className="mb-2 text-sm font-medium text-slate-500">
          Gyan Sarthi
        </p>

        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Welcome back 👋
        </h1>

        <p className="mt-2 max-w-2xl text-slate-500">
          Your AI-powered GATE CSE preparation workspace.
          Learn concepts, practice questions, revise weak
          areas, and track your exam readiness.
        </p>
      </section>

      {/* =====================================================
          ERROR
      ====================================================== */}
      {error && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm font-medium text-amber-800">
            Dashboard data could not be loaded.
          </p>

          <p className="mt-1 text-xs text-amber-700">
            {error}
          </p>
        </div>
      )}

      {/* =====================================================
          STATS
      ====================================================== */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Overall Mastery
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {adaptivePlan?.overall_mastery != null
                  ? `${Math.round(adaptivePlan.overall_mastery)}%`
                  : "--"}
              </p>
            </div>

            <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
              <Target size={20} />
            </div>
          </div>

          <p className="mt-4 text-xs text-slate-400">
            Based on your topic performance
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Accuracy
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {adaptivePlan?.accuracy != null
                  ? `${Math.round(adaptivePlan.accuracy)}%`
                  : "--"}
              </p>
            </div>

            <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
              <TrendingUp size={20} />
            </div>
          </div>

          <p className="mt-4 text-xs text-slate-400">
            From your recent attempts
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Readiness
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {adaptivePlan?.readiness_score != null
                  ? `${Math.round(adaptivePlan.readiness_score)}%`
                  : "--"}
              </p>
            </div>

            <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
              <Brain size={20} />
            </div>
          </div>

          <p className="mt-4 text-xs text-slate-400">
            Current exam readiness
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Study Streak
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {adaptivePlan?.study_streak != null
                  ? `${adaptivePlan.study_streak} days`
                  : "0 days"}
              </p>
            </div>

            <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
              <Flame size={20} />
            </div>
          </div>

          <p className="mt-4 text-xs text-slate-400">
            Keep your preparation consistent
          </p>
        </div>

      </section>

      {/* =====================================================
          TODAY'S FOCUS
      ====================================================== */}
      <section className="grid gap-6 lg:grid-cols-3">

        <div className="rounded-2xl border border-slate-200 bg-white p-6 lg:col-span-2">

          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Today's Focus
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Your adaptive preparation plan.
              </p>
            </div>

            <Clock3
              size={20}
              className="text-slate-400"
            />
          </div>

          {todayPlan ? (
            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-5">

              <div className="flex items-start gap-4">

                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-slate-700 shadow-sm">
                  <BookOpen size={21} />
                </div>

                <div className="min-w-0 flex-1">

                  <h3 className="font-semibold text-slate-900">
                    {todayPlan.title ||
                      todayPlan.topic_name ||
                      "Adaptive Study Session"}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {todayPlan.description ||
                      "Continue working on the topics identified by your learning profile."}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2">

                    {todayPlan.action && (
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">
                        {todayPlan.action}
                      </span>
                    )}

                    {todayPlan.question_count && (
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">
                        {todayPlan.question_count} questions
                      </span>
                    )}

                    {todayPlan.estimated_minutes && (
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">
                        {todayPlan.estimated_minutes} min
                      </span>
                    )}

                  </div>
                </div>

              </div>

            </div>
          ) : (
            <div className="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center">

              <Target
                size={30}
                className="mx-auto text-slate-400"
              />

              <h3 className="mt-3 font-semibold text-slate-800">
                Your learning plan starts here
              </h3>

              <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
                Complete a diagnostic or practice session
                to let Gyan Sarthi identify your strengths
                and weak topics.
              </p>

            </div>
          )}

        </div>

        {/* =====================================================
            AI TUTOR
        ====================================================== */}
        <div className="rounded-2xl bg-slate-900 p-6 text-white">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
            <Brain size={21} />
          </div>

          <h2 className="mt-5 text-xl font-bold">
            AI Tutor
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-300">
            Ask concepts, formulas, doubts, or exam
            questions. Get explanations grounded in your
            verified knowledge base.
          </p>

          <a
            href="/ai-tutor"
            className="mt-6 flex items-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-100"
          >
            Ask AI Tutor
            <ArrowRight size={17} />
          </a>

        </div>

      </section>

      {/* =====================================================
          SUBJECTS
      ====================================================== */}
      <section>

        <div className="mb-4">
          <h2 className="text-lg font-bold text-slate-900">
            GATE CSE Subjects
          </h2>

          <p className="text-sm text-slate-500">
            Build concept mastery across your preparation.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          {subjects.map((subject) => (
            <div
              key={subject.code}
              className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:-translate-y-0.5 hover:shadow-md"
            >

              <div className="flex items-center justify-between">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-sm font-bold text-slate-700">
                  {subject.code}
                </div>

                <ArrowRight
                  size={18}
                  className="text-slate-400"
                />

              </div>

              <h3 className="mt-4 font-semibold text-slate-800">
                {subject.name}
              </h3>

              <p className="mt-1 text-xs text-slate-400">
                Mastery will update from your attempts
              </p>

            </div>
          ))}

        </div>

      </section>

      {/* =====================================================
          ADAPTIVE PLAN
      ====================================================== */}
      {adaptivePlan && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
              <Brain size={20} />
            </div>

            <div>
              <h2 className="font-bold text-slate-900">
                Adaptive Learning Engine
              </h2>

              <p className="text-sm text-slate-500">
                Recommendations generated from your
                preparation data.
              </p>
            </div>

          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">

            {adaptivePlan.priority_topic && (
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Priority Topic
                </p>

                <p className="mt-2 font-semibold text-slate-800">
                  {adaptivePlan.priority_topic}
                </p>
              </div>
            )}

            {adaptivePlan.recommended_action && (
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Recommended Action
                </p>

                <p className="mt-2 font-semibold text-slate-800">
                  {adaptivePlan.recommended_action}
                </p>
              </div>
            )}

            {adaptivePlan.question_count && (
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Practice Load
                </p>

                <p className="mt-2 font-semibold text-slate-800">
                  {adaptivePlan.question_count} questions
                </p>
              </div>
            )}

          </div>

        </section>
      )}

      {/* =====================================================
          FOOTER STATUS
      ====================================================== */}
      <div className="flex items-center gap-2 pb-4 text-xs text-slate-400">
        <CheckCircle2 size={15} />
        Gyan Sarthi is using your latest learning activity
        to personalize recommendations.
      </div>

    </div>
  );
}