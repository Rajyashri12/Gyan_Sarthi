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
  Zap,
} from "lucide-react";

import {
  getAdaptivePractice,
  getPracticeQuestions,
  submitPracticeAnswer,
  type PracticeQuestion,
  type PracticeSubmitResponse,
} from "../../services/api/practice";

/* =========================================================
   CONFIGURATION
========================================================= */

const GATE_EXAM_ID = 1;

/* =========================================================
   SUBJECTS
========================================================= */

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

/* =========================================================
   DIFFICULTIES
========================================================= */

const DIFFICULTIES = [
  "all",
  "easy",
  "medium",
  "hard",
];

/* =========================================================
   TIME FORMAT
========================================================= */

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60);

  const remainingSeconds =
    seconds % 60;

  return `${String(minutes).padStart(
    2,
    "0",
  )}:${String(
    remainingSeconds,
  ).padStart(2, "0")}`;
}

/* =========================================================
   PRACTICE PAGE
========================================================= */

export default function Practice() {
  /* =======================================================
     STATE
  ======================================================== */

  const [
    selectedSubject,
    setSelectedSubject,
  ] = useState<string | null>(null);

  const [
    difficulty,
    setDifficulty,
  ] = useState("all");

  const [
    questions,
    setQuestions,
  ] = useState<PracticeQuestion[]>([]);

  const [
    currentIndex,
    setCurrentIndex,
  ] = useState(0);

  const [
    selectedAnswer,
    setSelectedAnswer,
  ] = useState("");

  const [
    confidence,
    setConfidence,
  ] = useState(3);

  const [
    elapsedSeconds,
    setElapsedSeconds,
  ] = useState(0);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    result,
    setResult,
  ] =
    useState<PracticeSubmitResponse | null>(
      null,
    );

  /* =======================================================
     CURRENT QUESTION
  ======================================================== */

  const currentQuestion =
    questions[currentIndex];

  /* =======================================================
     TIMER
  ======================================================== */

  useEffect(() => {
    if (
      !currentQuestion ||
      result
    ) {
      return;
    }

    const timer =
      window.setInterval(() => {
        setElapsedSeconds(
          (previous) =>
            previous + 1,
        );
      }, 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, [
    currentQuestion,
    result,
  ]);

  /* =======================================================
     RESET PRACTICE
  ======================================================== */

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

  /* =======================================================
     NORMAL PRACTICE
  ======================================================== */

  async function startPractice(
    subjectCode: string,
  ) {
    try {
      setLoading(true);

      setError("");

      setSelectedSubject(
        subjectCode,
      );

      const data =
        await getPracticeQuestions({
          subject_code:
            subjectCode,

          difficulty:
            difficulty === "all"
              ? undefined
              : difficulty,

          limit: 10,
        });

      console.log(
        "NORMAL PRACTICE RESPONSE:",
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

  /* =======================================================
     ADAPTIVE PRACTICE
  ======================================================== */

  async function startAdaptivePractice() {
    try {
      setLoading(true);

      setError("");

      console.log(
        "Starting adaptive practice...",
      );

      const data =
        await getAdaptivePractice({
          exam_id:
            GATE_EXAM_ID,

          limit: 10,
        });

      console.log(
        "ADAPTIVE PRACTICE RESPONSE:",
        data,
      );

      if (
        !data ||
        data.length === 0
      ) {
        setError(
          "No adaptive questions are available yet. Complete some practice questions first so Gyan Sarthi can build your learning profile.",
        );

        return;
      }

      /*
       * AdaptiveQuestion extends the same
       * question structure used by normal
       * practice.
       */

      const adaptiveQuestions: PracticeQuestion[] =
        data.map((question) => ({
          id: question.id,

          question_text:
            question.question_text,

          option_a:
            question.option_a,

          option_b:
            question.option_b,

          option_c:
            question.option_c,

          option_d:
            question.option_d,

          difficulty:
            question.difficulty,

          question_type:
            question.question_type,

          is_pyq:
            question.is_pyq,

          exam_year:
            question.exam_year,

          marks:
            question.marks,

          negative_marks:
            question.negative_marks,
        }));

      setSelectedSubject(
        "ADAPTIVE",
      );

      setQuestions(
        adaptiveQuestions,
      );

      setCurrentIndex(0);

      setSelectedAnswer("");

      setConfidence(3);

      setElapsedSeconds(0);

      setResult(null);
    } catch (err) {
      console.error(
        "Adaptive practice error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load adaptive practice.",
      );
    } finally {
      setLoading(false);
    }
  }

  /* =======================================================
     SUBMIT ANSWER
  ======================================================== */

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

      const payload = {
        question_id:
          currentQuestion.id,

        selected_answer:
          selectedAnswer,

        time_taken_seconds:
          elapsedSeconds,

        confidence,
      };

      console.log(
        "SUBMITTING ANSWER:",
        payload,
      );

      const response =
        await submitPracticeAnswer(
          payload,
        );

      console.log(
        "SUBMIT RESPONSE:",
        response,
      );

      setResult(response);
    } catch (err) {
      console.error(
        "Submit answer error:",
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

  /* =======================================================
     NEXT QUESTION
  ======================================================== */

  function nextQuestion() {
    const isLastQuestion =
      currentIndex >=
      questions.length - 1;

    if (isLastQuestion) {
      resetPractice();

      return;
    }

    setCurrentIndex(
      (previous) =>
        previous + 1,
    );

    setSelectedAnswer("");

    setConfidence(3);

    setElapsedSeconds(0);

    setResult(null);

    setError("");
  }

  /* =======================================================
     SUBJECT SELECTION SCREEN
  ======================================================== */

  if (!selectedSubject) {
    return (
      <div className="mx-auto max-w-7xl space-y-8">

        {/* =================================================
            HEADER
        ================================================== */}

        <section>
          <p className="text-sm font-medium text-slate-500">
            Gyan Sarthi
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            Practice
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Practice GATE CSE questions and
            build concept-level mastery
            through every attempt.
          </p>
        </section>

        {/* =================================================
            PRACTICE SETTINGS
        ================================================== */}

        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

            <div>
              <h2 className="font-semibold text-slate-900">
                Practice settings
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Choose a difficulty for
                normal practice.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">

              {DIFFICULTIES.map(
                (item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() =>
                      setDifficulty(
                        item,
                      )
                    }
                    className={[
                      "rounded-lg px-4 py-2 text-xs font-semibold capitalize transition",

                      difficulty ===
                      item
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

        {/* =================================================
            ERROR
        ================================================== */}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">
            {error}
          </div>
        )}

        {/* =================================================
            SUBJECT HEADER
        ================================================== */}

        <section>

          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Choose a subject
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Select a subject for normal
                practice or use Adaptive
                Practice.
              </p>
            </div>

            {/* Adaptive Button */}

            <button
              type="button"
              onClick={
                startAdaptivePractice
              }
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Zap size={17} />

              Adaptive Practice

              <ArrowRight size={16} />
            </button>

          </div>

          {/* =================================================
              SUBJECT CARDS
          ================================================== */}

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

        {/* =================================================
            HOW ADAPTIVE PRACTICE WORKS
        ================================================== */}

        <section className="rounded-2xl bg-slate-900 p-6 text-white">

          <div className="flex items-start gap-4">

            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/10">
              <Target size={21} />
            </div>

            <div>

              <h2 className="font-semibold">
                How Adaptive Practice works
              </h2>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                Gyan Sarthi uses your topic
                mastery, recent performance,
                mistakes and forgetting risk
                to determine what you should
                practice next.
              </p>

              <div className="mt-4 flex flex-wrap gap-2">

                {[
                  "Weak Topics",
                  "Recent Performance",
                  "Mistakes",
                  "Forgetting Risk",
                ].map(
                  (item) => (
                    <span
                      key={item}
                      className="rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium text-slate-200"
                    >
                      {item}
                    </span>
                  ),
                )}

              </div>

            </div>

          </div>

        </section>

      </div>
    );
  }

  /* =======================================================
     LOADING SCREEN
  ======================================================== */

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />

          <p className="mt-4 text-sm font-medium text-slate-600">
            {selectedSubject ===
            "ADAPTIVE"
              ? "Building your adaptive practice..."
              : "Loading practice questions..."}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Please wait.
          </p>

        </div>

      </div>
    );
  }

  /* =======================================================
     NO QUESTIONS
  ======================================================== */

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

        <p className="mt-2 text-sm leading-6 text-slate-500">
          There are currently no questions
          matching your selected practice
          mode.
        </p>

        {error && (
          <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-left text-sm text-red-700">
            {error}
          </div>
        )}

        <button
          type="button"
          onClick={resetPractice}
          className="mt-6 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
        >
          Back to Practice
        </button>

      </div>
    );
  }

  /* =======================================================
     QUESTION SCREEN
  ======================================================== */

  return (
    <div className="mx-auto max-w-4xl space-y-6">

      {/* =================================================
          TOP BAR
      ================================================== */}

      <div className="flex flex-wrap items-center justify-between gap-4">

        <button
          type="button"
          onClick={
            resetPractice
          }
          className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={17} />

          {selectedSubject ===
          "ADAPTIVE"
            ? "Exit adaptive practice"
            : "Exit practice"}
        </button>

        <div className="flex items-center gap-3">

          {/* Timer */}

          <div className="flex items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm font-medium text-slate-600 shadow-sm ring-1 ring-slate-200">
            <Clock3 size={17} />

            {formatTime(
              elapsedSeconds,
            )}
          </div>

          {/* Question counter */}

          <div className="rounded-xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white">
            {currentIndex + 1} /{" "}
            {questions.length}
          </div>

        </div>

      </div>

      {/* =================================================
          PROGRESS
      ================================================== */}

      <div className="h-2 overflow-hidden rounded-full bg-slate-200">

        <div
          className="h-full rounded-full bg-slate-900 transition-all duration-300"
          style={{
            width: `${
              ((currentIndex +
                1) /
                questions.length) *
              100
            }%`,
          }}
        />

      </div>

      {/* =================================================
          QUESTION CARD
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">

        {/* =================================================
            METADATA
        ================================================== */}

        <div className="flex flex-wrap gap-2">

          {/* Adaptive badge */}

          {selectedSubject ===
            "ADAPTIVE" && (
            <span className="flex items-center gap-1.5 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
              <Zap size={12} />

              Adaptive
            </span>
          )}

          {/* Difficulty */}

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium capitalize text-slate-600">
            {currentQuestion.difficulty}
          </span>

          {/* Question type */}

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {currentQuestion.question_type}
          </span>

          {/* PYQ */}

          {currentQuestion.is_pyq && (
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              GATE PYQ

              {currentQuestion.exam_year
                ? ` • ${currentQuestion.exam_year}`
                : ""}
            </span>
          )}

          {/* Marks */}

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {currentQuestion.marks}{" "}
            Mark
          </span>

        </div>

        {/* =================================================
            QUESTION TEXT
        ================================================== */}

        <h2 className="mt-6 text-xl font-semibold leading-8 text-slate-900 sm:text-2xl">
          {currentQuestion.question_text}
        </h2>

        {/* =================================================
            OPTIONS
        ================================================== */}

        <div className="mt-8 space-y-3">

          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Choose your answer
          </p>

          {[
            {
              key: "A",
              text:
                currentQuestion.option_a,
            },

            {
              key: "B",
              text:
                currentQuestion.option_b,
            },

            {
              key: "C",
              text:
                currentQuestion.option_c,
            },

            {
              key: "D",
              text:
                currentQuestion.option_d,
            },
          ].map((option) => {

            const isSelected =
              selectedAnswer ===
              option.key;

            return (
              <button
                key={option.key}
                type="button"
                disabled={Boolean(
                  result,
                )}
                onClick={() => {

                  console.log(
                    "OPTION CLICKED:",
                    option.key,
                  );

                  setSelectedAnswer(
                    option.key,
                  );
                }}
                className={[
                  "flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-all",

                  isSelected
                    ? "border-slate-900 bg-slate-900 text-white shadow-md"
                    : "border-slate-200 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50",

                  result
                    ? "cursor-default"
                    : "cursor-pointer",
                ].join(" ")}
              >

                {/* Letter */}

                <span
                  className={[
                    "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-sm font-bold",

                    isSelected
                      ? "bg-white text-slate-900"
                      : "bg-slate-100 text-slate-700",
                  ].join(" ")}
                >
                  {option.key}
                </span>

                {/* Option text */}

                <span className="text-sm font-medium leading-6">
                  {option.text ??
                    "Option unavailable"}
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

            <div className="flex items-center justify-between gap-4">

              <div>

                <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">
                  Confidence Level
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Rate your certainty to
                  feed the mistake
                  intelligence system
                  (1 = low, 5 = high).
                </p>

              </div>

              <Target
                size={21}
                className="shrink-0 text-slate-400"
              />

            </div>

            {/* Confidence buttons */}

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

                      confidence ===
                      value
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

        {/* =================================================
            ERROR
        ================================================== */}

        {error && (
          <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">
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

              {/* Icon */}

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

                {/* Result title */}

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

                {/* Correct answer */}

                <p className="mt-2 text-sm text-slate-700">
                  Correct answer:{" "}
                  <strong>
                    {
                      result.correct_answer
                    }
                  </strong>
                </p>

                {/* Marks */}

                <p className="mt-1 text-sm text-slate-700">
                  Marks awarded:{" "}
                  <strong>
                    {
                      result.marks_awarded
                    }
                  </strong>
                </p>

                {/* Explanation */}

                {result.explanation && (
                  <div className="mt-4 rounded-lg bg-white/70 p-4">

                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Explanation
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-700">
                      {
                        result.explanation
                      }
                    </p>

                  </div>
                )}

              </div>

            </div>

          </div>
        )}

        {/* =================================================
            ACTION BUTTON
        ================================================== */}

        <div className="mt-8 flex justify-end">

          {/* Submit */}

          {!result && (
            <button
              type="button"
              onClick={
                handleSubmit
              }
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
                <ArrowRight
                  size={17}
                />
              )}

            </button>
          )}

          {/* Next */}

          {result && (
            <button
              type="button"
              onClick={
                nextQuestion
              }
              className="flex items-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >

              {currentIndex ===
              questions.length -
                1
                ? "Finish Practice"
                : "Next Question"}

              <ArrowRight
                size={17}
              />

            </button>
          )}

        </div>

      </section>

      {/* =================================================
          FOOTER
      ================================================== */}

      <div className="flex items-center justify-center gap-2 pb-6 text-xs text-slate-400">

        <RotateCcw size={14} />

        Every attempt helps Gyan Sarthi
        update your learning profile.

      </div>

    </div>
  );
}