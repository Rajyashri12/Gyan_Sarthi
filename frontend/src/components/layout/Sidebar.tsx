import {
  BarChart3,
  BookOpen,
  Brain,
  CalendarClock,
  ClipboardCheck,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Settings,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const navigation = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Practice",
    path: "/practice",
    icon: BookOpen,
  },
  {
    name: "AI Tutor",
    path: "/ai-tutor",
    icon: Brain,
  },
  {
    name: "Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Revision",
    path: "/revision",
    icon: CalendarClock,
  },
  {
    name: "Exams",
    path: "/exams",
    icon: ClipboardCheck,
  },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      navigate("/login", { replace: true });
    }
  }

  const initials =
    user?.name
      ?.split(" ")
      .filter(Boolean)
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "GS";

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-slate-200 bg-white lg:flex lg:flex-col">

      {/* =====================================================
          BRAND
      ====================================================== */}
      <div className="flex h-20 shrink-0 items-center border-b border-slate-100 px-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
            <GraduationCap size={22} strokeWidth={2} />
          </div>

          <div className="min-w-0">
            <h1 className="truncate text-lg font-bold tracking-tight text-slate-900">
              Gyan Sarthi
            </h1>

            <p className="text-xs font-medium text-slate-400">
              AI Exam Companion
            </p>
          </div>
        </div>
      </div>

      {/* =====================================================
          NAVIGATION
      ====================================================== */}
      <nav className="flex-1 overflow-y-auto px-3 py-5">

        <p className="px-3 pb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Learning
        </p>

        <div className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  [
                    "group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      size={19}
                      strokeWidth={isActive ? 2.2 : 1.9}
                      className="shrink-0"
                    />

                    <span className="truncate">
                      {item.name}
                    </span>
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* =====================================================
            EXAM INFORMATION
        ====================================================== */}
        <div className="mt-8">
          <p className="px-3 pb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Current Exam
          </p>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-xs font-bold text-slate-700 shadow-sm">
                G
              </div>

              <div className="min-w-0">
                <p className="text-sm font-semibold text-slate-800">
                  GATE CSE
                </p>

                <p className="truncate text-xs text-slate-400">
                  Computer Science & Engineering
                </p>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* =====================================================
          USER PROFILE
      ====================================================== */}
      <div className="border-t border-slate-100 p-3">

        <div className="mb-2 flex items-center gap-3 rounded-xl px-3 py-3">
          {/* Avatar */}
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
            {initials}
          </div>

          {/* User details */}
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-slate-800">
              {user?.name || "Student"}
            </p>

            <p className="truncate text-xs text-slate-400">
              {user?.email || "GATE Aspirant"}
            </p>
          </div>
        </div>

        {/* Settings */}
        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <Settings
            size={19}
            strokeWidth={1.9}
          />

          <span>Settings</span>
        </button>

        {/* Logout */}
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-red-50 hover:text-red-600"
        >
          <LogOut
            size={19}
            strokeWidth={1.9}
          />

          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}