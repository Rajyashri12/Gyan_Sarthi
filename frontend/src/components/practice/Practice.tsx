import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Clock3,
  RotateCcw,
  Target,
  XCircle,
} from "lucide-react";

import {
  getPracticeQuestions,
  submitPracticeAnswer,
  type PracticeQuestion,
  type PracticeSubmitResponse,
} from "../../services/api/practice";

const SUBJECTS = [
  {
    code: "GA",
    name: "General Aptitude",
    description:
      "Verbal, quantitative and analytical aptitude",
  },
  {
    code: "DBMS",
    name: "Database Management Systems",
    description:
      "SQL, normalization, transactions and databases",
  },
  {
    code: "OS",
    name: "Operating Systems",
    description:
      "Processes, memory, scheduling and deadlocks",
  },
  {
    code: "CN",
    name: "Computer Networks",
    description:
      "TCP/IP, routing, transport and networking",
  },
];

const DIFFICULTIES = [
  "all",
  "easy",
  "medium",
  "hard",
];

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(
    remainingSeconds,
  ).padStart(2, "0")}`;
}

export default function Practice() {
  const [selectedSubject, setSelectedSubject] =
    useState<string | null>(null);

  const [difficulty, setDifficulty] =
    useState("all");

  const [questions, setQuestions] = useState<
    PracticeQuestion[]
  >([]);

  const [currentIndex, setCurrentIndex] =
    useState(0);

  const [selectedAnswer, setSelectedAnswer] =
    useState("");

  const [confidence, setConfidence] =
    useState(3);

  const [elapsedSeconds, setElapsedSeconds] =
    useState(0);

  const [loading, setLoading] =
    useState(false);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [result, setResult] =
    useState<PracticeSubmitResponse | null>(
      null,
    );

  const currentQuestion =
    questions[currentIndex];

  /* =====================================================
     TIMER
  ====================================================== */

  useEffect(() => {
    if (!currentQuestion || result) {
      return;
    }

    const timer = window.setInterval(() => {
      setElapsedSeconds(
        (previous) => previous + 1,
      );
    }, 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, [currentQuestion, result]);

  /* =====================================================
     START PRACTICE
  ====================================================== */

  async function startPractice(
    subjectCode: string,
  ) {
    try {
      setSelectedSubject(subjectCode);
      setLoading(true);
      setError("");

      const data =
        await getPracticeQuestions({
          subject_code: subjectCode,
          difficulty:
            difficulty === "all"
              ? undefined
              : difficulty,
          limit: 10,
        });

      console.log(
        "Practice API response:",
        data,
      );

      setQuestions(data);

      setCurrentIndex(0);
      setSelectedAnswer("");
      setConfidence(3);
      setElapsedSeconds(0);
      setResult(null);
    } catch (err) {
      console.error(
        "Practice loading error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load practice questions.",
      );
    } finally {
      setLoading(false);
    }
  }

  /* =====================================================
     RESET
  ====================================================== */

  function resetPractice() {
    setSelectedSubject(null);
    setQuestions([]);

    setCurrentIndex(0);
    setSelectedAnswer("");
    setConfidence(3);
    setElapsedSeconds(0);

    setResult(null);
    setError("");
  }

  /* =====================================================
     SUBMIT
  ====================================================== */

  async function handleSubmit() {
    if (
      !currentQuestion ||
      !selectedAnswer
    ) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      console.log(
        "Submitting answer:",
        {
          question_id:
            currentQuestion.id,
          selected_answer:
            selectedAnswer,
          time_taken_seconds:
            elapsedSeconds,
          confidence,
        },
      );

      const response =
        await submitPracticeAnswer({
          question_id:
            currentQuestion.id,

          selected_answer:
            selectedAnswer,

          time_taken_seconds:
            elapsedSeconds,

          confidence,
        });

      console.log(
        "Submit response:",
        response,
      );

      setResult(response);
    } catch (err) {
      console.error(
        "Submit error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to submit answer.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  /* =====================================================
     NEXT QUESTION
  ====================================================== */

  function nextQuestion() {
    if (
      currentIndex >=
      questions.length - 1
    ) {
      resetPractice();
      return;
    }

    setCurrentIndex(
      (previous) => previous + 1,
    );

    setSelectedAnswer("");
    setConfidence(3);
    setElapsedSeconds(0);
    setResult(null);
  }

  /* =====================================================
     SUBJECT SELECTION
  ====================================================== */

  if (!selectedSubject) {
    return (
      <div className="mx-auto max-w-7xl space-y-8">

        <section>
          <p className="text-sm font-medium text-slate-500">
            Gyan Sarthi
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            Practice
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Practice GATE CSE questions and
            build topic-level mastery through
            every attempt.
          </p>
        </section>

        {/* Difficulty */}
        <section className="rounded-2xl border border-slate-200 bg-white p-5">

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

            <div>
              <h2 className="font-semibold text-slate-900">
                Practice settings
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Choose a difficulty before
                starting.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">

              {DIFFICULTIES.map(
                (item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() =>
                      setDifficulty(item)
                    }
                    className={[
                      "rounded-lg px-4 py-2 text-xs font-semibold capitalize transition",
                      difficulty === item
                        ? "bg-slate-900 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200",
                    ].join(" ")}
                  >
                    {item}
                  </button>
                ),
              )}

            </div>
          </div>
        </section>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Subjects */}
        <section>

          <div className="mb-4">
            <h2 className="text-lg font-bold text-slate-900">
              Choose a subject
            </h2>

            <p className="text-sm text-slate-500">
              Select where you want to practice.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {SUBJECTS.map(
              (subject) => (
                <button
                  key={subject.code}
                  type="button"
                  disabled={loading}
                  onClick={() =>
                    startPractice(
                      subject.code,
                    )
                  }
                  className="group rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:border-slate-300 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60"
                >

                  <div className="flex items-center justify-between">

                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-sm font-bold text-slate-700">
                      {subject.code}
                    </div>

                    <ArrowRight
                      size={18}
                      className="text-slate-400 transition group-hover:translate-x-1"
                    />

                  </div>

                  <h3 className="mt-5 font-semibold text-slate-900">
                    {subject.name}
                  </h3>

                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    {subject.description}
                  </p>

                </button>
              ),
            )}

          </div>

        </section>

      </div>
    );
  }

  /* =====================================================
     LOADING
  ====================================================== */

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />

          <p className="mt-4 text-sm text-slate-500">
            Loading practice questions...
          </p>

        </div>

      </div>
    );
  }

  /* =====================================================
     NO QUESTIONS
  ====================================================== */

  if (!currentQuestion) {
    return (
      <div className="mx-auto max-w-2xl py-16 text-center">

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
          <BookOpen
            size={26}
            className="text-slate-600"
          />
        </div>

        <h1 className="mt-5 text-2xl font-bold text-slate-900">
          No questions available
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          There are currently no questions
          matching your selection.
        </p>

        <button
          type="button"
          onClick={resetPractice}
          className="mt-6 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
        >
          Choose another subject
        </button>

      </div>
    );
  }

  /* =====================================================
     QUESTION SCREEN
  ====================================================== */

  return (
    <div className="mx-auto max-w-4xl space-y-6">

      {/* Top bar */}
      <div className="flex flex-wrap items-center justify-between gap-4">

        <button
          type="button"
          onClick={resetPractice}
          className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={17} />
          Exit practice
        </button>

        <div className="flex items-center gap-3">

          <div className="flex items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm text-slate-600 shadow-sm ring-1 ring-slate-200">
            <Clock3 size={17} />
            {formatTime(
              elapsedSeconds,
            )}
          </div>

          <div className="rounded-xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white">
            {currentIndex + 1} /{" "}
            {questions.length}
          </div>

        </div>

      </div>

      {/* Progress */}
      <div className="h-2 overflow-hidden rounded-full bg-slate-200">

        <div
          className="h-full rounded-full bg-slate-900 transition-all"
          style={{
            width: `${
              ((currentIndex + 1) /
                questions.length) *
              100
            }%`,
          }}
        />

      </div>

      {/* Question card */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">

        {/* Metadata */}
        <div className="flex flex-wrap gap-2">

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium capitalize text-slate-600">
            {currentQuestion.difficulty}
          </span>

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {currentQuestion.question_type}
          </span>

          {currentQuestion.is_pyq && (
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              GATE PYQ
              {currentQuestion.exam_year
                ? ` • ${currentQuestion.exam_year}`
                : ""}
            </span>
          )}

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {currentQuestion.marks} Mark
          </span>

        </div>

        {/* Question */}
        <h2 className="mt-6 text-xl font-semibold leading-8 text-slate-900">
          {currentQuestion.question_text}
        </h2>

        {/* =================================================
            OPTIONS
        ================================================== */}

        <div className="mt-8 space-y-3">

          {[
            {
              key: "A",
              text: currentQuestion.option_a,
            },
            {
              key: "B",
              text: currentQuestion.option_b,
            },
            {
              key: "C",
              text: currentQuestion.option_c,
            },
            {
              key: "D",
              text: currentQuestion.option_d,
            },
          ].map((option) => {

            if (!option.text) {
              return null;
            }

            const isSelected =
              selectedAnswer ===
              option.key;

            return (
              <button
                key={option.key}
                type="button"
                disabled={Boolean(result)}
                onClick={() => {
                  console.log(
                    "Selected:",
                    option.key,
                  );

                  setSelectedAnswer(
                    option.key,
                  );
                }}
                className={[
                  "flex w-full items-start gap-4 rounded-xl border p-4 text-left transition-all",
                  isSelected
                    ? "border-slate-900 bg-slate-50 shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50",
                  result
                    ? "cursor-default"
                    : "cursor-pointer",
                ].join(" ")}
              >

                {/* Letter */}
                <span
                  className={[
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-bold transition",
                    isSelected
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-700",
                  ].join(" ")}
                >
                  {option.key}
                </span>

                {/* Text */}
                <span className="pt-1 text-sm leading-6 text-slate-700">
                  {option.text}
                </span>

              </button>
            );
          })}

        </div>

        {/* =================================================
            CONFIDENCE
        ================================================== */}

        {!result && (
          <div className="mt-8 rounded-xl bg-slate-50 p-5">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">
                  Confidence Level
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Rate your certainty to feed mistake
                  intelligence models (1 = low, 5 = high).
                </p>
              </div>

              <Target
                size={21}
                className="text-slate-400"
              />

            </div>

            <div className="mt-4 grid grid-cols-5 gap-2">

              {[1, 2, 3, 4, 5].map(
                (value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() =>
                      setConfidence(
                        value,
                      )
                    }
                    className={[
                      "rounded-lg border py-3 text-sm font-semibold transition",
                      confidence === value
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-200 bg-white text-slate-600 hover:bg-slate-100",
                    ].join(" ")}
                  >
                    {value}
                  </button>
                ),
              )}

            </div>

          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* =================================================
            RESULT
        ================================================== */}

        {result && (
          <div
            className={[
              "mt-6 rounded-xl border p-5",
              result.is_correct
                ? "border-emerald-200 bg-emerald-50"
                : "border-red-200 bg-red-50",
            ].join(" ")}
          >

            <div className="flex items-start gap-3">

              {result.is_correct ? (
                <CheckCircle2
                  size={23}
                  className="mt-0.5 shrink-0 text-emerald-600"
                />
              ) : (
                <XCircle
                  size={23}
                  className="mt-0.5 shrink-0 text-red-600"
                />
              )}

              <div className="min-w-0">

                <h3
                  className={[
                    "font-semibold",
                    result.is_correct
                      ? "text-emerald-800"
                      : "text-red-800",
                  ].join(" ")}
                >
                  {result.is_correct
                    ? "Correct answer"
                    : "Incorrect answer"}
                </h3>

                <p className="mt-2 text-sm text-slate-700">
                  Correct answer:{" "}
                  <strong>
                    {result.correct_answer}
                  </strong>
                </p>

                <p className="mt-1 text-sm text-slate-700">
                  Marks awarded:{" "}
                  <strong>
                    {result.marks_awarded}
                  </strong>
                </p>

                {result.explanation && (
                  <div className="mt-4 rounded-lg bg-white/70 p-4">

                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Explanation
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-700">
                      {result.explanation}
                    </p>

                  </div>
                )}

              </div>

            </div>

          </div>
        )}

        {/* =================================================
            SUBMIT / NEXT
        ================================================== */}

        <div className="mt-8 flex justify-end">

          {!result ? (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={
                !selectedAnswer ||
                submitting
              }
              className={[
                "flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold transition",
                selectedAnswer &&
                !submitting
                  ? "bg-slate-900 text-white hover:bg-slate-800"
                  : "cursor-not-allowed bg-slate-300 text-slate-500",
              ].join(" ")}
            >
              {submitting
                ? "Submitting..."
                : "Submit Answer"}

              {!submitting && (
                <ArrowRight size={17} />
              )}
            </button>
          ) : (
            <button
              type="button"
              onClick={nextQuestion}
              className="flex items-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >
              {currentIndex ===
              questions.length - 1
                ? "Finish Practice"
                : "Next Question"}

              <ArrowRight size={17} />
            </button>
          )}

        </div>

      </section>

      {/* Footer */}
      <div className="flex items-center justify-center gap-2 pb-6 text-xs text-slate-400">
        <RotateCcw size={14} />

        Every attempt helps Gyan Sarthi update
        your learning profile.
      </div>

    </div>
  );
}