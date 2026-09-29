import { Bell, Search } from "lucide-react";

export default function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6 lg:px-8">

      <div>
        <p className="text-sm font-semibold text-slate-800">
          GATE CSE
        </p>

        <p className="text-xs text-slate-400">
          Preparation workspace
        </p>
      </div>

      <div className="flex items-center gap-2">

        <button className="rounded-xl p-2.5 text-slate-500 hover:bg-slate-100">
          <Search size={20} />
        </button>

        <button className="relative rounded-xl p-2.5 text-slate-500 hover:bg-slate-100">

          <Bell size={20} />

          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />

        </button>

        <div className="ml-2 flex items-center gap-3 border-l border-slate-200 pl-4">

          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white">
            GS
          </div>

          <div className="hidden sm:block">

            <p className="text-sm font-semibold text-slate-800">
              Student
            </p>

            <p className="text-xs text-slate-400">
              GATE Aspirant
            </p>

          </div>

        </div>

      </div>
    </header>
  );
}