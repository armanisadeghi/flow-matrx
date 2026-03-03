import { Link, useLocation } from "react-router";
import { GitBranch, ChevronLeft, ChevronRight } from "lucide-react";
import { useLayoutStore } from "../../stores/layoutStore";
import { cn } from "../../lib/utils";

const NAV_ITEMS = [
  { to: "/", label: "Workflows", icon: GitBranch },
] as const;

export default function Sidebar() {
  const collapsed = useLayoutStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useLayoutStore((s) => s.toggleSidebar);
  const location = useLocation();

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-slate-700 bg-slate-800 transition-all duration-200 shrink-0",
        collapsed ? "w-11" : "w-48",
      )}
    >
      <nav className="flex-1 py-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
          const active = location.pathname === to || (to !== "/" && location.pathname.startsWith(to));
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 text-sm transition-colors",
                active
                  ? "text-indigo-400 bg-slate-700/50"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/30",
              )}
            >
              <Icon size={16} className="shrink-0" />
              {!collapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>
      <button
        type="button"
        onClick={toggleSidebar}
        className="p-2.5 border-t border-slate-700 text-slate-500 hover:text-slate-300 transition-colors"
      >
        {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </aside>
  );
}
