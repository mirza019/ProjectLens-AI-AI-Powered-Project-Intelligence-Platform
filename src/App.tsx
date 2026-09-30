import { useEffect, useMemo, useState } from "react";
import {
  LayoutDashboard,
  FolderKanban,
  ChartNoAxesCombined,
  TrendingUp,
  ShieldAlert,
  FileText,
  Library,
  MessageSquareText,
  Lightbulb,
  ClipboardCheck,
  Users,
  Scale,
  Workflow,
  Settings,
  LogOut,
  PanelLeftClose,
  Sparkles,
  Search,
  X,
  Command,
  ChevronRight,
} from "lucide-react";
import { Sidebar } from "./layout/Sidebar";
import { Topbar } from "./components";
import { Overview } from "./pages/Overview";
import { ProjectsPage } from "./pages/Projects";
import { ModulePages } from "./pages/Modules";
import { Assistant } from "./pages/Assistant";
import { Login } from "./pages/Login";
import type { LucideIcon } from "lucide-react";
import { api, clearSession, type SessionUser } from "./services/api";

type NavItem = [string, string, LucideIcon];
type NavGroup = { group: string; items: NavItem[] };
export const nav: NavGroup[] = [
  {
    group: "INTELLIGENCE",
    items: [
      ["overview", "Overview", LayoutDashboard],
      ["projects", "Projects", FolderKanban],
      ["financials", "Financial Performance", ChartNoAxesCombined],
      ["forecasts", "Forecasts", TrendingUp],
      ["risks", "Risks", ShieldAlert],
    ],
  },
  {
    group: "KNOWLEDGE",
    items: [
      ["contracts", "Contracts", FileText],
      ["knowledge", "Project Knowledge", Library],
      ["assistant", "AI Assistant", MessageSquareText],
    ],
  },
  {
    group: "TRANSFORMATION",
    items: [
      ["opportunities", "AI Opportunities", Lightbulb],
      ["reports", "Reports", ClipboardCheck],
      ["adoption", "Adoption", Users],
      ["governance", "Governance", Scale],
      ["pipeline", "Data Pipeline", Workflow],
    ],
  },
  { group: "SYSTEM", items: [["settings", "Settings", Settings]] },
];

export default function App() {
  const [user, setUser] = useState<SessionUser | null>(() => {
    try {
      return JSON.parse(localStorage.getItem("pl-user") || "null");
    } catch {
      return null;
    }
  });
  const [page, setPage] = useState("overview");
  const [collapsed, setCollapsed] = useState(false);
  const [search, setSearch] = useState(false);
  const [riskCount, setRiskCount] = useState(0);
  useEffect(() => {
    if (user)
      api
        .risks()
        .then((rows) => setRiskCount(rows.length))
        .catch(() => setRiskCount(0));
  }, [user]);
  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearch(true);
      }
      if (e.key === "Escape") setSearch(false);
    };
    addEventListener("keydown", fn);
    return () => removeEventListener("keydown", fn);
  }, []);
  const title = useMemo(
    () =>
      nav.flatMap((g) => g.items).find((x) => x[0] === page)?.[1] || "Overview",
    [page],
  );
  if (!user) return <Login onLogin={setUser} />;
  let content =
    page === "overview" ? (
      <Overview onNavigate={setPage} />
    ) : page === "projects" ? (
      <ProjectsPage />
    ) : page === "assistant" ? (
      <Assistant />
    ) : (
      <ModulePages page={page} />
    );
  return (
    <div className={`shell ${collapsed ? "collapsed" : ""}`}>
      <Sidebar
        page={page}
        setPage={setPage}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        onLogout={() => {
          clearSession();
          setUser(null);
        }}
        riskCount={riskCount}
      />
      <div className="app">
        <Topbar onSearch={() => setSearch(true)} />
        <main key={page}>{content}</main>
        <footer>
          <span>
            Synthetic demonstration data — no companies or contracts are real.
          </span>
          <span>{user.role} · ProjectLens AI v2.0</span>
        </footer>
      </div>
      {search && (
        <SearchModal
          close={() => setSearch(false)}
          go={(p) => {
            setPage(p);
            setSearch(false);
          }}
        />
      )}
    </div>
  );
}

function SearchModal({
  close,
  go,
}: {
  close: () => void;
  go: (p: string) => void;
}) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<any[]>([]);
  useEffect(() => {
    if (q.trim().length < 2) return setResults([]);
    const timer = window.setTimeout(() => api.search(q).then(setResults), 180);
    return () => window.clearTimeout(timer);
  }, [q]);
  const items = nav
    .flatMap((g) => g.items)
    .filter((i) => i[1].toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="modal-backdrop" onMouseDown={close}>
      <div className="command" onMouseDown={(e) => e.stopPropagation()}>
        <div className="command-input">
          <Search />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search projects, risks, contracts, reports…"
          />
          <button onClick={close}>
            <X />
          </button>
        </div>
        <div className="command-label">QUICK NAVIGATION</div>
        {items.slice(0, 6).map(([id, label, Icon]) => (
          <button className="command-item" onClick={() => go(id)} key={id}>
            <Icon />
            <span>
              {label}
              <small>Open {label.toLowerCase()}</small>
            </span>
            <ChevronRight />
          </button>
        ))}
        {results.length > 0 && (
          <div className="command-label">WORKSPACE RESULTS</div>
        )}
        {results.slice(0, 8).map((result) => (
          <button
            className="command-item"
            key={result.id}
            onClick={() =>
              go(
                result.type === "Risk"
                  ? "risks"
                  : result.type === "Contract"
                    ? "contracts"
                    : result.type === "Document"
                      ? "knowledge"
                      : "projects",
              )
            }
          >
            <Search />
            <span>
              {result.title}
              <small>
                {result.type} · {result.detail}
              </small>
            </span>
            <ChevronRight />
          </button>
        ))}
        <div className="command-foot">
          <span>
            <Command /> K to open
          </span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
}
