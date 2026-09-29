import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Flag,
  Send,
} from "lucide-react";

import {
  saveExamAnswer,
  submitExam,
  type ExamQuestion,
  type ExamResultResponse,
} from "../../services/api/exam";

type Props = {
  sessionId: number;
  exam: {
    session_id: number;
    exam_id: number;
    total_questions: number;
    duration_minutes: number;
    started_at: string;
    questions: ExamQuestion[];
  };
  onSubmitted: (
    result: ExamResultResponse,
  ) => void;
};

const options = [
  "A",
  "B",
  "C",
  "D",
];

function getOptionText(
  question: ExamQuestion,
  option: string,
) {
  switch (option) {
    case "A":
      return question.option_a;

    case "B":
      return question.option_b;

    case "C":
      return question.option_c;

    case "D":
      return question.option_d;

    default:
      return null;
  }
}

function formatTime(
  seconds: number,
) {
  const safeSeconds =
    Math.max(0, seconds);

  const minutes =
    Math.floor(
      safeSeconds / 60,
    );

  const remaining =
    safeSeconds % 60;

  return `${String(
    minutes,
  ).padStart(2, "0")}:${String(
    remaining,
  ).padStart(2, "0")}`;
}

export default function ExamSession({
  sessionId,
  exam,
  onSubmitted,
}: Props) {
  const [
    currentIndex,
    setCurrentIndex,
  ] = useState(0);

  const [
    answers,
    setAnswers,
  ] = useState<
    Record<number, string | null>
  >({});

  const [
    marked,
    setMarked,
  ] = useState<
    Record<number, boolean>
  >({});

  const [
    questionTimes,
    setQuestionTimes,
  ] = useState<
    Record<number, number>
  >({});

  const [
    elapsedSeconds,
    setElapsedSeconds,
  ] = useState(0);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    showSubmitDialog,
    setShowSubmitDialog,
  ] = useState(false);

  const questions =
    exam.questions;

  const question =
    questions[currentIndex];

  const remainingSeconds =
    Math.max(
      0,
      exam.duration_minutes *
        60 -
        elapsedSeconds,
    );

  /* =======================================================
     TIMER
  ======================================================== */

  useEffect(() => {
    const timer =
      window.setInterval(() => {
        setElapsedSeconds(
          (previous) =>
            previous + 1,
        );
      }, 1000);

    return () =>
      window.clearInterval(
        timer,
      );
  }, []);

  /* =======================================================
     AUTO SUBMIT
  ======================================================== */

  useEffect(() => {
    if (
      remainingSeconds <= 0 &&
      !submitting
    ) {
      handleSubmitExam();
    }
  }, [
    remainingSeconds,
    submitting,
  ]);

  /* =======================================================
     CURRENT QUESTION TIME
  ======================================================== */

  useEffect(() => {
    const questionId =
      question?.id;

    if (!questionId) {
      return;
    }

    const timer =
      window.setInterval(() => {
        setQuestionTimes(
          (previous) => ({
            ...previous,

            [questionId]:
              (previous[
                questionId
              ] || 0) + 1,
          }),
        );
      }, 1000);

    return () =>
      window.clearInterval(
        timer,
      );
  }, [
    question?.id,
  ]);

  /* =======================================================
     ANSWER
  ======================================================== */

  async function handleSelectAnswer(
    selected: string,
  ) {
    if (!question) {
      return;
    }

    const updatedAnswers = {
      ...answers,
      [question.id]:
        selected,
    };

    setAnswers(
      updatedAnswers,
    );

    const timeTaken =
      questionTimes[
        question.id
      ] || 0;

    try {
      await saveExamAnswer(
        sessionId,
        {
          question_id:
            question.id,

          selected_answer:
            selected,

          time_taken_seconds:
            timeTaken,
        },
      );
    } catch (err) {
      console.error(
        "Answer save error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Answer could not be saved.",
      );
    }
  }

  /* =======================================================
     CLEAR ANSWER
  ======================================================== */

  async function clearAnswer() {
    if (!question) {
      return;
    }

    setAnswers(
      (previous) => ({
        ...previous,
        [question.id]:
          null,
      }),
    );

    try {
      await saveExamAnswer(
        sessionId,
        {
          question_id:
            question.id,

          selected_answer:
            null,

          time_taken_seconds:
            questionTimes[
              question.id
            ] || 0,
        },
      );
    } catch (err) {
      console.error(
        err,
      );
    }
  }

  /* =======================================================
     NAVIGATION
  ======================================================== */

  function goNext() {
    if (
      currentIndex <
      questions.length - 1
    ) {
      setCurrentIndex(
        (index) =>
          index + 1,
      );
    }
  }

  function goPrevious() {
    if (
      currentIndex > 0
    ) {
      setCurrentIndex(
        (index) =>
          index - 1,
      );
    }
  }

  /* =======================================================
     SUBMIT
  ======================================================== */

  async function handleSubmitExam() {
    if (submitting) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const result =
        await submitExam(
          sessionId,
        );

      console.log(
        "EXAM RESULT:",
        result,
      );

      onSubmitted(result);
    } catch (err) {
      console.error(
        "Exam submit error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to submit exam.",
      );

      setSubmitting(false);
    }
  }

  /* =======================================================
     COUNTS
  ======================================================== */

  const attemptedCount =
    useMemo(
      () =>
        Object.values(
          answers,
        ).filter(Boolean)
          .length,
      [answers],
    );

  const markedCount =
    useMemo(
      () =>
        Object.values(
          marked,
        ).filter(Boolean)
          .length,
      [marked],
    );

  if (!question) {
    return (
      <div className="p-8 text-center">
        No questions found.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">

      {/* TOP BAR */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white">

        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-4 px-4 py-4">

          <div>

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              GATE CSE
            </p>

            <h1 className="mt-1 text-lg font-bold text-slate-900">
              Exam Simulation
            </h1>

          </div>

          <div className="flex items-center gap-3">

            <div className="hidden text-right sm:block">

              <p className="text-[10px] uppercase tracking-wide text-slate-400">
                Progress
              </p>

              <p className="text-sm font-bold text-slate-800">
                {attemptedCount}/
                {questions.length}
              </p>

            </div>

            <div
              className={[
                "flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold",

                remainingSeconds <=
                60
                  ? "bg-red-100 text-red-700"
                  : "bg-slate-100 text-slate-800",
              ].join(" ")}
            >
              <Clock3
                size={17}
              />

              {formatTime(
                remainingSeconds,
              )}
            </div>

          </div>

        </div>

      </header>

      {/* ERROR */}

      {error && (
        <div className="mx-auto mt-4 max-w-[1500px] px-4">

          <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>

        </div>
      )}

      {/* MAIN */}

      <main className="mx-auto grid max-w-[1500px] gap-6 p-4 lg:grid-cols-[1fr_320px]">

        {/* QUESTION */}

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 p-6">

            <div className="flex items-center justify-between gap-4">

              <div>

                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Question{" "}
                  {currentIndex +
                    1}{" "}
                  of{" "}
                  {questions.length}
                </p>

                <p className="mt-2 text-xs text-slate-500">
                  {question.question_type}{" "}
                  ·{" "}
                  {question.difficulty}
                </p>

              </div>

              <button
                type="button"
                onClick={() =>
                  setMarked(
                    (previous) => ({
                      ...previous,
                      [question.id]:
                        !previous[
                          question.id
                        ],
                    }),
                  )
                }
                className={[
                  "flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold",

                  marked[
                    question.id
                  ]
                    ? "border-amber-300 bg-amber-50 text-amber-700"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50",
                ].join(" ")}
              >
                <Flag size={15} />

                {marked[
                  question.id
                ]
                  ? "Marked"
                  : "Mark for Review"}
              </button>

            </div>

          </div>

          <div className="p-6">

            <h2 className="text-lg font-semibold leading-8 text-slate-900">
              {question.question_text}
            </h2>

            <div className="mt-8 space-y-3">

              {options.map(
                (option) => {
                  const text =
                    getOptionText(
                      question,
                      option,
                    );

                  if (!text) {
                    return null;
                  }

                  const selected =
                    answers[
                      question.id
                    ] ===
                    option;

                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() =>
                        handleSelectAnswer(
                          option,
                        )
                      }
                      className={[
                        "flex w-full items-start gap-4 rounded-xl border p-4 text-left transition",

                        selected
                          ? "border-slate-900 bg-slate-900 text-white"
                          : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50",
                      ].join(" ")}
                    >
                      <span
                        className={[
                          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold",

                          selected
                            ? "bg-white text-slate-900"
                            : "bg-slate-100 text-slate-600",
                        ].join(" ")}
                      >
                        {option}
                      </span>

                      <span className="pt-1 text-sm leading-6">
                        {text}
                      </span>

                    </button>
                  );
                },
              )}

            </div>

            <div className="mt-5">

              <button
                type="button"
                onClick={
                  clearAnswer
                }
                disabled={
                  !answers[
                    question.id
                  ]
                }
                className="text-xs font-semibold text-slate-500 hover:text-slate-900 disabled:opacity-40"
              >
                Clear response
              </button>

            </div>

          </div>

          {/* NAVIGATION */}

          <div className="flex items-center justify-between border-t border-slate-100 p-5">

            <button
              type="button"
              onClick={
                goPrevious
              }
              disabled={
                currentIndex ===
                0
              }
              className="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft
                size={17}
              />

              Previous
            </button>

            {currentIndex <
            questions.length -
              1 ? (
              <button
                type="button"
                onClick={
                  goNext
                }
                className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Next

                <ChevronRight
                  size={17}
                />
              </button>
            ) : (
              <button
                type="button"
                onClick={() =>
                  setShowSubmitDialog(
                    true,
                  )
                }
                className="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700"
              >
                <Send size={16} />

                Submit Exam
              </button>
            )}

          </div>

        </section>

        {/* PALETTE */}

        <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:h-fit lg:sticky lg:top-24">

          <div>

            <h2 className="font-bold text-slate-900">
              Question Palette
            </h2>

            <p className="mt-1 text-xs text-slate-400">
              Navigate between questions.
            </p>

          </div>

          <div className="mt-5 grid grid-cols-5 gap-2">

            {questions.map(
              (
                item,
                index,
              ) => {
                const answered =
                  Boolean(
                    answers[
                      item.id
                    ],
                  );

                const isMarked =
                  Boolean(
                    marked[
                      item.id
                    ],
                  );

                const current =
                  index ===
                  currentIndex;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() =>
                      setCurrentIndex(
                        index,
                      )
                    }
                    className={[
                      "relative flex h-10 items-center justify-center rounded-lg border text-xs font-bold",

                      current
                        ? "border-slate-900 bg-slate-900 text-white"
                        : answered
                          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                          : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50",
                    ].join(" ")}
                  >
                    {index + 1}

                    {isMarked && (
                      <span className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full bg-amber-500" />
                    )}

                  </button>
                );
              },
            )}

          </div>

          <div className="mt-6 space-y-3 border-t border-slate-100 pt-5">

            <Legend
              className="bg-emerald-50 border-emerald-200"
              label="Answered"
            />

            <Legend
              className="bg-white border-slate-200"
              label="Not Answered"
            />

            <Legend
              className="bg-slate-900 border-slate-900"
              label="Current"
            />

            <Legend
              className="bg-amber-50 border-amber-300"
              label="Marked for Review"
            />

          </div>

          <div className="mt-6 rounded-xl bg-slate-50 p-4">

            <p className="text-xs text-slate-500">
              Attempted
            </p>

            <p className="mt-1 text-xl font-bold text-slate-900">
              {attemptedCount}
            </p>

            <p className="mt-3 text-xs text-slate-500">
              Marked
            </p>

            <p className="mt-1 text-xl font-bold text-slate-900">
              {markedCount}
            </p>

          </div>

          <button
            type="button"
            onClick={() =>
              setShowSubmitDialog(
                true,
              )
            }
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 hover:bg-red-100"
          >
            <Send size={15} />

            Submit Exam
          </button>

        </aside>

      </main>

      {/* SUBMIT DIALOG */}

      {showSubmitDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">

          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">

            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50">
              <AlertTriangle
                size={22}
                className="text-amber-600"
              />
            </div>

            <h2 className="mt-5 text-xl font-bold text-slate-900">
              Submit Exam?
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              You have attempted{" "}
              <strong>
                {attemptedCount}
              </strong>{" "}
              of{" "}
              <strong>
                {questions.length}
              </strong>{" "}
              questions.
              {questions.length -
                attemptedCount >
                0 &&
                " Unanswered questions will be submitted as unanswered."}
            </p>

            <div className="mt-6 flex gap-3">

              <button
                type="button"
                onClick={() =>
                  setShowSubmitDialog(
                    false,
                  )
                }
                className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Continue Exam
              </button>

              <button
                type="button"
                onClick={
                  handleSubmitExam
                }
                disabled={
                  submitting
                }
                className="flex-1 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
              >
                {submitting
                  ? "Submitting..."
                  : "Submit Now"}
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}

/* =========================================================
   LEGEND
========================================================= */

function Legend({
  className,
  label,
}: {
  className: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-3">

      <span
        className={`h-4 w-4 rounded border ${className}`}
      />

      <span className="text-xs text-slate-500">
        {label}
      </span>

    </div>
  );
}