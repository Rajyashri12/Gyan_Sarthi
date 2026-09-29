import { useState } from "react";
import type { FormEvent } from "react";
import { ArrowRight, GraduationCap, Lock, Mail } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();

  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const from =
    (location.state as { from?: string } | null)?.from ||
    "/dashboard";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed. Please check your credentials.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f6f8fc]">
      <div className="grid min-h-screen lg:grid-cols-2">

        {/* Left branding */}
        <div className="hidden bg-slate-900 p-12 text-white lg:flex lg:flex-col lg:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-slate-900">
                <GraduationCap size={24} />
              </div>

              <div>
                <h1 className="text-xl font-bold">
                  Gyan Sarthi
                </h1>
                <p className="text-xs text-slate-400">
                  AI Exam Companion
                </p>
              </div>
            </div>

            <div className="mt-24 max-w-lg">
              <p className="text-sm font-medium text-slate-400">
                GATE CSE Preparation
              </p>

              <h2 className="mt-4 text-5xl font-bold leading-tight">
                Learn smarter.
                <br />
                Practice better.
                <br />
                Prepare with confidence.
              </h2>

              <p className="mt-6 max-w-md leading-7 text-slate-400">
                Build concept mastery, identify weak areas,
                practice intelligently and track your exam
                readiness with Gyan Sarthi.
              </p>
            </div>
          </div>

          <p className="text-xs text-slate-500">
            Gyan Sarthi • AI-powered adaptive learning
          </p>
        </div>

        {/* Login */}
        <div className="flex items-center justify-center px-5 py-12 sm:px-8">
          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="mb-10 flex items-center gap-3 lg:hidden">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
                <GraduationCap size={24} />
              </div>

              <div>
                <h1 className="text-xl font-bold text-slate-900">
                  Gyan Sarthi
                </h1>
                <p className="text-xs text-slate-500">
                  AI Exam Companion
                </p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-slate-500">
                Welcome back
              </p>

              <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                Sign in to your account
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Continue your GATE CSE preparation.
              </p>
            </div>

            <form
              onSubmit={handleSubmit}
              className="mt-8 space-y-5"
            >
              {/* Email */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Email address
                </label>

                <div className="relative">
                  <Mail
                    size={18}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  />

                  <input
                    type="email"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    placeholder="you@example.com"
                    required
                    autoComplete="email"
                    className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Password
                </label>

                <div className="relative">
                  <Lock
                    size={18}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  />

                  <input
                    type="password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                    className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                  />
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={submitting}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? (
                  "Signing in..."
                ) : (
                  <>
                    Sign in
                    <ArrowRight size={17} />
                  </>
                )}
              </button>
            </form>

            <p className="mt-8 text-center text-sm text-slate-500">
              Don't have an account?{" "}
              <Link
                to="/register"
                className="font-semibold text-slate-900 hover:underline"
              >
                Create account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}