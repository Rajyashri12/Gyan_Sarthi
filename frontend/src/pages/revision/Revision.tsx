import { useEffect, useMemo, useState } from "react";

import {
  AlertCircle,
  CalendarClock,
  CheckCircle2,
  Clock3,
  RefreshCw,
  RotateCcw,
  Target,
} from "lucide-react";

import {
  completeRevision,
  getDueRevisions,
  getRevisionDashboard,
  getUpcomingRevisions,
  type Revision as RevisionItem,
  type RevisionCompleteResponse,
} from "../../services/api/revision";

/* =========================================================
   HELPERS
========================================================= */

function formatDate(
  value: string,
) {
  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    },
  );
}

function formatDateTime(
  value: string,
) {
  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    },
  );
}

function formatStatus(
  status: string,
) {
  return status
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

function statusClass(
  status: string,
) {
  switch (
    status.toLowerCase()
  ) {
    case "completed":
      return "bg-emerald-50 text-emerald-700";

    case "due":
      return "bg-red-50 text-red-700";

    case "scheduled":
      return "bg-blue-50 text-blue-700";

    default:
      return "bg-slate-100 text-slate-600";
  }
}

/* =========================================================
   REVISION PAGE
========================================================= */

export default function Revision() {
  const [
    dueRevisions,
    setDueRevisions,
  ] = useState<RevisionItem[]>([]);

  const [
    dashboardRevisions,
    setDashboardRevisions,
  ] = useState<RevisionItem[]>([]);

  const [
    upcomingRevisions,
    setUpcomingRevisions,
  ] = useState<RevisionItem[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    completingId,
    setCompletingId,
  ] = useState<number | null>(
    null,
  );

  const [
    selectedRevision,
    setSelectedRevision,
  ] =
    useState<RevisionItem | null>(
      null,
    );

  const [
    recallScore,
    setRecallScore,
  ] = useState(3);

  const [
    completedResult,
    setCompletedResult,
  ] =
    useState<RevisionCompleteResponse | null>(
      null,
    );

  const [
    error,
    setError,
  ] = useState("");

  /* =======================================================
     LOAD DATA
  ======================================================== */

  async function loadRevisionData() {
    try {
      setLoading(true);

      setError("");

      const [
        due,
        dashboard,
        upcoming,
      ] = await Promise.all([
        getDueRevisions(),

        getRevisionDashboard(),

        getUpcomingRevisions(7),
      ]);

      console.log(
        "DUE REVISIONS:",
        due,
      );

      console.log(
        "REVISION DASHBOARD:",
        dashboard,
      );

      console.log(
        "UPCOMING REVISIONS:",
        upcoming,
      );

      setDueRevisions(due);

      setDashboardRevisions(
        dashboard,
      );

      setUpcomingRevisions(
        upcoming,
      );
    } catch (err) {
      console.error(
        "Revision loading error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load revisions.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRevisionData();
  }, []);

  /* =======================================================
     COUNTS
  ======================================================== */

  const scheduledCount =
    useMemo(() => {
      return dashboardRevisions.filter(
        (item) =>
          item.status.toLowerCase() ===
          "scheduled",
      ).length;
    }, [dashboardRevisions]);

  /* =======================================================
     START REVISION
  ======================================================== */

  function startRevision(
    revision: RevisionItem,
  ) {
    setSelectedRevision(
      revision,
    );

    setRecallScore(3);

    setCompletedResult(null);

    setError("");
  }

  /* =======================================================
     COMPLETE REVISION
  ======================================================== */

  async function handleCompleteRevision() {
    if (!selectedRevision) {
      return;
    }

    try {
      setCompletingId(
        selectedRevision.revision_id,
      );

      setError("");

      console.log(
        "COMPLETING REVISION:",
        {
          revision_id:
            selectedRevision.revision_id,

          recall_score:
            recallScore,
        },
      );

      const response =
        await completeRevision(
          selectedRevision.revision_id,
          recallScore,
        );

      console.log(
        "REVISION COMPLETE RESPONSE:",
        response,
      );

      setCompletedResult(
        response,
      );

      /*
       * Reload the lists because
       * completing a revision can create
       * the next revision.
       */

      await loadRevisionData();
    } catch (err) {
      console.error(
        "Revision completion error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to complete revision.",
      );
    } finally {
      setCompletingId(null);
    }
  }

  /* =======================================================
     LOADING
  ======================================================== */

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />

          <p className="mt-4 text-sm font-medium text-slate-600">
            Loading revision schedule...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Preparing your revision plan.
          </p>

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
              Revision
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Review topics at the right time
              and strengthen concepts before
              they are forgotten.
            </p>

          </div>

          <button
            type="button"
            onClick={
              loadRevisionData
            }
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
          >
            <RefreshCw size={16} />
            Refresh
          </button>

        </div>

      </section>

      {/* =================================================
          ERROR
      ================================================== */}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4">

          <div className="flex items-start gap-3">

            <AlertCircle
              size={20}
              className="mt-0.5 shrink-0 text-red-600"
            />

            <p className="text-sm leading-6 text-red-700">
              {error}
            </p>

          </div>

        </div>
      )}

      {/* =================================================
          SUMMARY CARDS
      ================================================== */}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <SummaryCard
          title="Due Now"
          value={
            dueRevisions.length
          }
          description="Topics waiting for revision"
          icon={AlertCircle}
        />

        <SummaryCard
          title="Upcoming"
          value={
            upcomingRevisions.length
          }
          description="Scheduled in next 7 days"
          icon={CalendarClock}
        />

        <SummaryCard
          title="Scheduled"
          value={scheduledCount}
          description="Active revision schedule"
          icon={Clock3}
        />

        <SummaryCard
          title="Total Tracked"
          value={
            dashboardRevisions.length
          }
          description="Revision records"
          icon={Target}
        />

      </section>

      {/* =================================================
          COMPLETED RESULT
      ================================================== */}

      {completedResult && (
        <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

          <div className="flex items-start gap-4">

            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white">
              <CheckCircle2
                size={23}
                className="text-emerald-600"
              />
            </div>

            <div>

              <h2 className="font-bold text-emerald-900">
                Revision completed
              </h2>

              <p className="mt-1 text-sm text-emerald-700">
                Recall score:{" "}
                <strong>
                  {
                    completedResult.recall_score
                  }
                </strong>
              </p>

              {completedResult.next_revision_at && (
                <p className="mt-2 text-sm text-emerald-700">
                  Next revision:{" "}
                  <strong>
                    {formatDateTime(
                      completedResult.next_revision_at,
                    )}
                  </strong>
                </p>
              )}

            </div>

          </div>

        </section>
      )}

      {/* =================================================
          DUE REVISIONS
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between gap-4">

          <div>

            <h2 className="text-lg font-bold text-slate-900">
              Due Revisions
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              These topics are ready to be
              reviewed now.
            </p>

          </div>

          <AlertCircle
            size={21}
            className="text-slate-400"
          />

        </div>

        {dueRevisions.length ===
        0 ? (
          <EmptyRevisionState
            title="No revisions due"
            description="You're caught up. Check your upcoming schedule for the next review."
          />
        ) : (
          <div className="mt-6 grid gap-4 md:grid-cols-2">

            {dueRevisions.map(
              (revision) => (
                <RevisionCard
                  key={
                    revision.revision_id
                  }
                  revision={
                    revision
                  }
                  due
                  onStart={
                    startRevision
                  }
                />
              ),
            )}

          </div>
        )}

      </section>

      {/* =================================================
          UPCOMING
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between">

          <div>

            <h2 className="text-lg font-bold text-slate-900">
              Upcoming Revisions
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Your next scheduled reviews.
            </p>

          </div>

          <CalendarClock
            size={21}
            className="text-slate-400"
          />

        </div>

        {upcomingRevisions.length ===
        0 ? (
          <EmptyRevisionState
            title="No upcoming revisions"
            description="New revision sessions will appear as your mastery data develops."
          />
        ) : (
          <div className="mt-6 overflow-x-auto">

            <table className="w-full min-w-[650px]">

              <thead>

                <tr className="border-b border-slate-100 text-left">

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Topic
                  </th>

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Scheduled
                  </th>

                  <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Status
                  </th>

                  <th className="pb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Action
                  </th>

                </tr>

              </thead>

              <tbody>

                {upcomingRevisions.map(
                  (revision) => (
                    <tr
                      key={
                        revision.revision_id
                      }
                      className="border-b border-slate-50 last:border-0"
                    >

                      <td className="py-4 pr-4">

                        <p className="font-semibold text-slate-800">
                          {revision.topic}
                        </p>

                      </td>

                      <td className="py-4 pr-4">

                        <p className="text-sm text-slate-600">
                          {formatDate(
                            revision.scheduled_at,
                          )}
                        </p>

                      </td>

                      <td className="py-4 pr-4">

                        <span
                          className={`rounded-full px-3 py-1.5 text-xs font-semibold ${statusClass(
                            revision.status,
                          )}`}
                        >
                          {formatStatus(
                            revision.status,
                          )}
                        </span>

                      </td>

                      <td className="py-4">

                        <button
                          type="button"
                          onClick={() =>
                            startRevision(
                              revision,
                            )
                          }
                          className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Review
                        </button>

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
          REVISION DASHBOARD
      ================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

        <div>

          <h2 className="text-lg font-bold text-slate-900">
            Revision Dashboard
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            All revision records currently
            tracked by Gyan Sarthi.
          </p>

        </div>

        {dashboardRevisions.length ===
        0 ? (
          <EmptyRevisionState
            title="No revision records yet"
            description="Complete practice and mastery assessment to start building your revision schedule."
          />
        ) : (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

            {dashboardRevisions.map(
              (revision) => (
                <RevisionCard
                  key={
                    revision.revision_id
                  }
                  revision={
                    revision
                  }
                  onStart={
                    startRevision
                  }
                />
              ),
            )}

          </div>
        )}

      </section>

      {/* =================================================
          HOW IT WORKS
      ================================================== */}

      <section className="rounded-2xl bg-slate-900 p-6 text-white">

        <div className="flex items-start gap-4">

          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/10">
            <RotateCcw size={21} />
          </div>

          <div>

            <h2 className="font-bold">
              Spaced Revision
            </h2>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              Gyan Sarthi uses your mastery and
              recall performance to determine
              when a topic should be reviewed
              again. After completing a revision,
              your recall score influences the
              next scheduled review.
            </p>

          </div>

        </div>

      </section>

      {/* =================================================
          REVISION MODAL
      ================================================== */}

      {selectedRevision && (
        <RevisionModal
          revision={
            selectedRevision
          }
          recallScore={
            recallScore
          }
          setRecallScore={
            setRecallScore
          }
          completing={
            completingId ===
            selectedRevision.revision_id
          }
          completed={
            Boolean(
              completedResult,
            )
          }
          onComplete={
            handleCompleteRevision
          }
          onClose={() => {
            if (
              completingId ===
              null
            ) {
              setSelectedRevision(
                null,
              );

              setCompletedResult(
                null,
              );
            }
          }}
        />
      )}

    </div>
  );
}

/* =========================================================
   SUMMARY CARD
========================================================= */

function SummaryCard({
  title,
  value,
  description,
  icon: Icon,
}: {
  title: string;
  value: number;
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
   REVISION CARD
========================================================= */

function RevisionCard({
  revision,
  due = false,
  onStart,
}: {
  revision: RevisionItem;
  due?: boolean;
  onStart: (
    revision: RevisionItem,
  ) => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 transition hover:border-slate-300 hover:shadow-sm">

      <div className="flex items-start justify-between gap-4">

        <div className="min-w-0">

          <p className="truncate text-base font-semibold text-slate-900">
            {revision.topic}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Scheduled{" "}
            {formatDate(
              revision.scheduled_at,
            )}
          </p>

        </div>

        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase ${
            due
              ? "bg-red-50 text-red-700"
              : statusClass(
                  revision.status,
                )
          }`}
        >
          {due
            ? "Due"
            : formatStatus(
                revision.status,
              )}
        </span>

      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">

        <MiniValue
          label="Mastery"
          value={`${revision.mastery_score.toFixed(
            0,
          )}%`}
        />

        <MiniValue
          label="Forgetting Risk"
          value={`${revision.forgetting_risk.toFixed(
            0,
          )}%`}
        />

        <MiniValue
          label="Mistakes"
          value={
            revision.mistake_count
          }
        />

        <MiniValue
          label="Priority"
          value={`${revision.priority_score.toFixed(
            0,
          )}`}
        />

      </div>

      <button
        type="button"
        onClick={() =>
          onStart(revision)
        }
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-800"
      >
        <RotateCcw size={16} />

        Start Revision
      </button>

    </div>
  );
}

/* =========================================================
   MINI VALUE
========================================================= */

function MiniValue({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">

      <p className="text-[10px] font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-bold text-slate-700">
        {value}
      </p>

    </div>
  );
}

/* =========================================================
   REVISION MODAL
========================================================= */

function RevisionModal({
  revision,
  recallScore,
  setRecallScore,
  completing,
  completed,
  onComplete,
  onClose,
}: {
  revision: RevisionItem;

  recallScore: number;

  setRecallScore: (
    value: number,
  ) => void;

  completing: boolean;

  completed: boolean;

  onComplete: () => void;

  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">

      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">

        <div className="flex items-start justify-between gap-4">

          <div>

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Revision Session
            </p>

            <h2 className="mt-2 text-xl font-bold text-slate-900">
              {revision.topic}
            </h2>

          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={completing}
            className="rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-100 disabled:opacity-50"
          >
            Close
          </button>

        </div>

        {/* Topic information */}

        <div className="mt-6 grid grid-cols-2 gap-3">

          <MiniValue
            label="Mastery"
            value={`${revision.mastery_score.toFixed(
              0,
            )}%`}
          />

          <MiniValue
            label="Forgetting Risk"
            value={`${revision.forgetting_risk.toFixed(
              0,
            )}%`}
          />

        </div>

        {!completed ? (
          <>
            {/* Recall */}

            <div className="mt-7">

              <p className="text-sm font-semibold text-slate-800">
                How well could you recall this
                topic?
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Rate your recall from 1
                (couldn't recall) to 5
                (fully recalled).
              </p>

              <div className="mt-4 grid grid-cols-5 gap-2">

                {[1, 2, 3, 4, 5].map(
                  (value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() =>
                        setRecallScore(
                          value,
                        )
                      }
                      className={[
                        "rounded-xl border py-3 text-sm font-bold transition",

                        recallScore ===
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

              <div className="mt-3 flex justify-between text-[10px] text-slate-400">
                <span>
                  Very weak
                </span>

                <span>
                  Excellent
                </span>
              </div>

            </div>

            {/* Complete */}

            <button
              type="button"
              onClick={
                onComplete
              }
              disabled={
                completing
              }
              className="mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {completing ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />

                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle2
                    size={17}
                  />

                  Complete Revision
                </>
              )}
            </button>
          </>
        ) : (
          <div className="mt-7 rounded-xl bg-emerald-50 p-5 text-center">

            <CheckCircle2
              size={30}
              className="mx-auto text-emerald-600"
            />

            <p className="mt-3 font-semibold text-emerald-800">
              Revision recorded
            </p>

            <button
              type="button"
              onClick={onClose}
              className="mt-4 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white"
            >
              Done
            </button>

          </div>
        )}

      </div>

    </div>
  );
}

/* =========================================================
   EMPTY STATE
========================================================= */

function EmptyRevisionState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="py-12 text-center">

      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100">
        <CalendarClock
          size={23}
          className="text-slate-400"
        />
      </div>

      <h3 className="mt-4 font-semibold text-slate-800">
        {title}
      </h3>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
        {description}
      </p>

    </div>
  );
}