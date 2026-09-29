import { useState } from "react";
import type { FormEvent } from "react";
import {
  ArrowRight,
  GraduationCap,
  Lock,
  Mail,
  User,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../../services/api/client";

export default function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await apiRequest("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          password,
        }),
      });

      navigate("/login", {
        replace: true,
        state: {
          message: "Account created successfully. Please sign in.",
        },
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f6f8fc] px-5 py-12">
      <div className="w-full max-w-md">

        <div className="mb-8 flex items-center gap-3">
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

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-medium text-slate-500">
            Get started
          </p>

          <h2 className="mt-2 text-3xl font-bold text-slate-900">
            Create your account
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Start your personalized GATE CSE preparation.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-7 space-y-5"
          >
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Full name
              </label>

              <div className="relative">
                <User
                  size={18}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />

                <input
                  type="text"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  placeholder="Your name"
                  required
                  className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                />
              </div>
            </div>

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
                  className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                />
              </div>
            </div>

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
                  placeholder="Create a password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                />
              </div>

              <p className="mt-2 text-xs text-slate-400">
                Use at least 8 characters.
              </p>
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? (
                "Creating account..."
              ) : (
                <>
                  Create account
                  <ArrowRight size={17} />
                </>
              )}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-semibold text-slate-900 hover:underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}