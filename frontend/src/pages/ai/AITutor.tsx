import { useState } from "react";
import type { FormEvent } from "react";
import {
  Bot,
  CheckCircle2,
  BookOpen,
  Send,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";

import {
  explainQuestion,
  type AIExplanationResponse,
} from "../../services/api/ai";

const suggestions = [
  "Explain normalization in DBMS",
  "What is a deadlock in Operating Systems?",
  "Explain TCP three-way handshake",
  "Solve a percentages problem",
];

export default function AITutor() {
  const [question, setQuestion] = useState("");
  const [subject, setSubject] = useState("DBMS");

  const [response, setResponse] =
    useState<AIExplanationResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event?: FormEvent<HTMLFormElement>,
  ) {
    event?.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const result = await explainQuestion({
        question: trimmedQuestion,
        subject_code: subject,
      });

      setResponse(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "AI Tutor could not generate a response.",
      );
    } finally {
      setLoading(false);
    }
  }

  function useSuggestion(text: string) {
    setQuestion(text);
    setError("");
  }

  function clearConversation() {
    setQuestion("");
    setResponse(null);
    setError("");
  }

  const confidence =
    response?.verification?.confidence_score ?? 0;

  const confidencePercent = Math.round(
    confidence * 100,
  );

  const verificationStatus =
    response?.verification?.status || "";

  const isVerified =
    verificationStatus === "VERIFIED";

  return (
    <div className="mx-auto max-w-6xl">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
            <Sparkles size={16} />
            Gyan Sarthi AI
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            AI Tutor
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Ask questions about GATE CSE concepts and get
            evidence-grounded explanations with verification.
          </p>
        </div>

        {response && (
          <button
            type="button"
            onClick={clearConversation}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            <RotateCcw size={16} />
            New Question
          </button>
        )}
      </div>


      {/* ================================================= */}
      {/* ASK CARD */}
      {/* ================================================= */}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="mb-5 flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Bot size={22} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">
              Ask Gyan Sarthi
            </h2>

            <p className="text-sm text-slate-500">
              Your verified GATE CSE learning assistant
            </p>
          </div>

        </div>


        {/* Subject */}

        <div className="mb-5">

          <label className="mb-2 block text-sm font-medium text-slate-700">
            Subject
          </label>

          <select
            value={subject}
            onChange={(event) =>
              setSubject(event.target.value)
            }
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100 sm:w-64"
          >
            <option value="GA">
              General Aptitude
            </option>

            <option value="DBMS">
              DBMS
            </option>

            <option value="OS">
              Operating Systems
            </option>

            <option value="CN">
              Computer Networks
            </option>
          </select>

        </div>


        {/* Question */}

        <form onSubmit={handleSubmit}>

          <label className="mb-2 block text-sm font-medium text-slate-700">
            What do you want to learn?
          </label>

          <div className="relative">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Example: Explain normalization and why 3NF is needed..."
              rows={5}
              className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 pr-14 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white focus:ring-2 focus:ring-slate-100"
            />

            <button
              type="submit"
              disabled={
                loading ||
                !question.trim()
              }
              className="absolute bottom-3 right-3 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Send size={17} />
            </button>

          </div>

        </form>


        {/* ================================================= */}
        {/* SUGGESTIONS */}
        {/* ================================================= */}

        <div className="mt-5">

          <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Try asking
          </p>

          <div className="grid gap-2 sm:grid-cols-2">

            {suggestions.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() =>
                  useSuggestion(item)
                }
                className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-600 transition hover:border-slate-300 hover:bg-slate-50"
              >
                {item}
              </button>
            ))}

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* ERROR */}
      {/* ================================================= */}

      {error && (
        <div className="mt-6 flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-5">

          <AlertTriangle
            size={20}
            className="mt-0.5 shrink-0 text-red-600"
          />

          <div>
            <p className="font-semibold text-red-800">
              AI Tutor request failed
            </p>

            <p className="mt-1 text-sm text-red-700">
              {error}
            </p>
          </div>

        </div>
      )}


      {/* ================================================= */}
      {/* LOADING */}
      {/* ================================================= */}

      {loading && (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

          <div className="flex items-center gap-4">

            <div className="flex h-11 w-11 animate-pulse items-center justify-center rounded-xl bg-slate-100">
              <Bot
                size={22}
                className="text-slate-500"
              />
            </div>

            <div className="flex-1">

              <div className="h-4 w-40 animate-pulse rounded bg-slate-200" />

              <div className="mt-3 h-3 w-full animate-pulse rounded bg-slate-100" />

              <div className="mt-2 h-3 w-4/5 animate-pulse rounded bg-slate-100" />

            </div>

          </div>

          <p className="mt-5 text-sm text-slate-500">
            Retrieving knowledge and verifying the explanation...
          </p>

        </div>
      )}


      {/* ================================================= */}
      {/* RESPONSE */}
      {/* ================================================= */}

      {response && !loading && (
        <div className="mt-6 space-y-5">

          {/* Answer */}

          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-100 px-6 py-5">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
                  <Bot
                    size={20}
                    className="text-slate-700"
                  />
                </div>

                <div>
                  <p className="font-semibold text-slate-900">
                    Gyan Sarthi Tutor
                  </p>

                  <p className="text-xs text-slate-500">
                    AI-generated explanation
                  </p>
                </div>

              </div>

            </div>


            <div className="px-6 py-6">

              <div className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
                {response.answer}
              </div>

            </div>

          </div>


          {/* ================================================= */}
          {/* VERIFICATION */}
          {/* ================================================= */}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">

              <div className="flex gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">

                  {isVerified ? (
                    <CheckCircle2
                      size={21}
                      className="text-emerald-600"
                    />
                  ) : (
                    <ShieldCheck
                      size={21}
                      className="text-slate-600"
                    />
                  )}

                </div>

                <div>

                  <h3 className="font-semibold text-slate-900">
                    Verification
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {verificationStatus ||
                      "Verification completed"}
                  </p>

                </div>

              </div>


              <div className="rounded-xl bg-slate-50 px-4 py-3">

                <p className="text-xs font-medium text-slate-500">
                  Confidence
                </p>

                <p className="mt-1 text-xl font-bold text-slate-900">
                  {confidencePercent}%
                </p>

              </div>

            </div>


            {/* Verification scores */}

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">

              <Score
                label="Facts"
                value={response.verification.fact_score}
              />

              <Score
                label="Formula"
                value={response.verification.formula_score}
              />

              <Score
                label="Code"
                value={response.verification.code_score}
              />

              <Score
                label="Citation"
                value={
                  response.verification.citation_score
                }
              />

              <Score
                label="Hallucination"
                value={
                  response.verification.hallucination_score
                }
              />

            </div>


            {/* Issues */}

            {response.verification.issues?.length > 0 && (
              <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">

                <p className="text-sm font-semibold text-amber-900">
                  Verification notes
                </p>

                <ul className="mt-2 space-y-1 text-sm text-amber-800">

                  {response.verification.issues.map(
                    (issue, index) => (
                      <li key={index}>
                        • {issue}
                      </li>
                    ),
                  )}

                </ul>

              </div>
            )}

          </div>


          {/* ================================================= */}
          {/* SOURCES */}
          {/* ================================================= */}

          {response.sources?.length > 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
                  <BookOpen
                    size={20}
                    className="text-slate-700"
                  />
                </div>

                <div>
                  <h3 className="font-semibold text-slate-900">
                    Knowledge Sources
                  </h3>

                  <p className="text-sm text-slate-500">
                    Retrieved sources used for the response
                  </p>
                </div>

              </div>


              <div className="mt-5 space-y-2">

                {response.sources.map(
                  (source, index) => (
                    <div
                      key={`${source}-${index}`}
                      className="flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-3"
                    >

                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white">
                        <BookOpen
                          size={15}
                          className="text-slate-500"
                        />
                      </div>

                      <span className="text-sm text-slate-700">
                        {source}
                      </span>

                    </div>
                  ),
                )}

              </div>

            </div>
          )}

        </div>
      )}

    </div>
  );
}


// ============================================================
// SCORE COMPONENT
// ============================================================

function Score({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  const percent = Math.round(
    Math.max(0, Math.min(1, value)) * 100,
  );

  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">

      <div className="flex items-center justify-between">

        <span className="text-xs font-medium text-slate-500">
          {label}
        </span>

        <span className="text-sm font-bold text-slate-800">
          {percent}%
        </span>

      </div>

      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-200">

        <div
          className="h-full rounded-full bg-slate-800 transition-all"
          style={{
            width: `${percent}%`,
          }}
        />

      </div>

    </div>
  );
}