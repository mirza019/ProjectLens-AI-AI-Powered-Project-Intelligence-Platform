import { PanelLeftClose, Sparkles, LogOut } from "lucide-react";
import { nav } from "../App";

export function Sidebar({
  page,
  setPage,
  collapsed,
  setCollapsed,
  onLogout,
  riskCount,
}: {
  page: string;
  setPage: (p: string) => void;
  collapsed: boolean;
  setCollapsed: (v: boolean) => void;
  onLogout: () => void;
  riskCount: number;
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="logo">
          <Sparkles />
        </div>
        <span>
          <b>ProjectLens</b>
          <em>AI</em>
        </span>
        <button onClick={() => setCollapsed(!collapsed)}>
          <PanelLeftClose />
        </button>
      </div>
      <nav>
        {nav.map((g) => (
          <div className="nav-group" key={g.group}>
            <label>{g.group}</label>
            {g.items.map(([id, name, Icon]) => (
              <button
                title={name}
                className={page === id ? "active" : ""}
                key={id}
                onClick={() => setPage(id)}
              >
                <Icon />
                <span>{name}</span>
                {id === "risks" && riskCount > 0 && <i>{riskCount}</i>}
                {id === "assistant" && <small>AI</small>}
              </button>
            ))}
          </div>
        ))}
      </nav>
      <div className="sidebar-foot">
        <div className="demo-note">
          <b>SYNTHETIC DATA</b>
          <span>Demonstration environment</span>
        </div>
        <button className="logout" onClick={onLogout}>
          <LogOut />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
