import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";

import { useState } from "react";

import AppLayout from "./components/layout/AppLayout";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

import Dashboard from "./pages/dashboard/Dashboard";
import Analytics from "./pages/analytics/Analytics";
import Revision from "./pages/revision/Revision";
import Practice from "./pages/practice/Practice";
import AITutor from "./pages/ai/AITutor";

import Exams from "./pages/exam/Exams";
import ExamSession from "./pages/exam/ExamSession";
import ExamResult from "./pages/exam/ExamResult";

import type {
  ExamResultResponse,
  ExamStartResponse,
} from "./services/api/exam";


// ============================================================
// EXAM PAGE
// ============================================================

function ExamPage() {
  const navigate = useNavigate();

  return (
    <Exams
      onExamStarted={(exam) => {
        navigate(`/exam/session/${exam.session_id}`, {
          state: exam,
        });
      }}
    />
  );
}


// ============================================================
// EXAM SESSION PAGE
// ============================================================

function ExamSessionPage() {
  const { sessionId } = useParams();

  const navigate = useNavigate();

  const [exam] = useState<ExamStartResponse | null>(() => {
    const stored = localStorage.getItem("gyan_sarthi_exam");

    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  });

  if (!exam || !sessionId) {
    return (
      <div className="p-8">
        <p className="text-slate-600">
          Exam session could not be loaded.
        </p>

        <button
          onClick={() => navigate("/exams")}
          className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-white"
        >
          Back to Exams
        </button>
      </div>
    );
  }

  return (
    <ExamSession
      sessionId={Number(sessionId)}
      exam={exam}
      onSubmitted={(result) => {
        localStorage.setItem(
          "gyan_sarthi_exam_result",
          JSON.stringify(result),
        );

        navigate(`/exam/result/${result.session_id}`, {
          state: result,
        });
      }}
    />
  );
}


// ============================================================
// EXAM RESULT PAGE
// ============================================================

function ExamResultPage() {
  const navigate = useNavigate();

  const stored = localStorage.getItem(
    "gyan_sarthi_exam_result",
  );

  if (!stored) {
    return (
      <div className="p-8">
        <p className="text-slate-600">
          Exam result could not be loaded.
        </p>

        <button
          onClick={() => navigate("/exams")}
          className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-white"
        >
          Back to Exams
        </button>
      </div>
    );
  }

  let result: ExamResultResponse;

  try {
    result = JSON.parse(stored);
  } catch {
    return (
      <div className="p-8">
        Invalid exam result.
      </div>
    );
  }

  return (
    <ExamResult
      result={result}
      onBack={() => navigate("/exams")}
      onRetake={() => navigate("/exams")}
    />
  );
}


// ============================================================
// APP
// ============================================================

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================================================== */}
        {/* AUTH ROUTES */}
        {/* ================================================== */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />


        {/* ================================================== */}
        {/* MAIN APPLICATION */}
        {/* ================================================== */}

        <Route element={<AppLayout />}>

          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/practice"
            element={
              <Practice />
            }
          />

          <Route
            path="/ai-tutor"
            element={
              <AITutor />
            }
          />

          <Route
            path="/analytics"
            element={<Analytics />}
          />

          <Route
            path="/revision"
            element={<Revision />}
          />

          <Route
            path="/exams"
            element={<ExamPage />}
          />

        </Route>


        {/* ================================================== */}
        {/* EXAM SESSION */}
        {/* ================================================== */}

        <Route
          path="/exam/session/:sessionId"
          element={<ExamSessionPage />}
        />


        {/* ================================================== */}
        {/* EXAM RESULT */}
        {/* ================================================== */}

        <Route
          path="/exam/result/:sessionId"
          element={<ExamResultPage />}
        />


        {/* ================================================== */}
        {/* UNKNOWN ROUTES */}
        {/* ================================================== */}

        <Route
          path="*"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />
        

      </Routes>
    </BrowserRouter>
  );
}