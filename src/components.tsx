import React, { useState } from "react";
import {
  ArrowUpRight,
  Search,
  Bell,
  Sparkles,
  ChevronDown,
  CircleAlert,
  CheckCircle2,
  Clock3,
  X,
} from "lucide-react";
import type { Health } from "./types";

export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone.toLowerCase()}`}>{children}</span>;
}
export function StatusBadge({ status }: { status: Health | string }) {
  const icon =
    status === "Healthy" ? (
      <CheckCircle2 />
    ) : status === "Critical" ? (
      <CircleAlert />
    ) : (
      <Clock3 />
    );
  return (
    <span className={`status ${status.toLowerCase()}`}>
      {icon}
      {status}
    </span>
  );
}
export function Card({
  children,
  className = "",
  title,
  action,
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
  action?: React.ReactNode;
}) {
  return (
    <section className={`card ${className}`}>
      {title && (
        <div className="card-head">
          <h3>{title}</h3>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
export function Kpi({
  label,
  value,
  delta,
  detail,
  alert = false,
}: {
  label: string;
  value: string;
  delta?: string;
  detail: string;
  alert?: boolean;
}) {
  return (
    <Card className="kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      <div className={`kpi-detail ${alert ? "negative" : ""}`}>
        {delta && <b>{delta}</b>} {detail}
      </div>
    </Card>
  );
}
export function PageHeader({
  eyebrow = "Portfolio intelligence",
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {actions && <div className="header-actions">{actions}</div>}
    </div>
  );
}
export function Topbar({ onSearch }: { onSearch: () => void }) {
  const [menu, setMenu] = useState<"org" | "alerts" | "profile" | null>(null);
  return (
    <header className="topbar">
      <button
        className="org"
        onClick={() => setMenu(menu === "org" ? null : "org")}
      >
        <span className="org-mark">PL</span>
        <span>
          <small>ORGANIZATION</small>ProjectLens Demo
        </span>
        <ChevronDown />
      </button>
      <div className="top-actions">
        <button className="search" onClick={onSearch}>
          <Search />
          <span>Search workspace</span>
          <kbd>⌘ K</kbd>
        </button>
        <span className="ai-online">
          <Sparkles /> AI online
        </span>
        <button
          className="icon-btn"
          onClick={() => setMenu(menu === "alerts" ? null : "alerts")}
        >
          <Bell />
          <i />
        </button>
        <button
          className="avatar"
          onClick={() => setMenu(menu === "profile" ? null : "profile")}
        >
          MR
        </button>
        <div className="user">
          <b>Maya Riedel</b>
          <small>Portfolio Director</small>
        </div>
        <ChevronDown className="chev" />
      </div>
      {menu && (
        <div className="top-popover">
          {menu === "org" && (
            <>
              <b>ProjectLens Demo</b>
              <small>Synthetic enterprise workspace</small>
              <button onClick={() => setMenu(null)}>
                Current organization ✓
              </button>
            </>
          )}
            {menu === "alerts" && (
              <>
                <b>Notifications</b>
                <button onClick={() => setMenu(null)}>Forecast commentary ready for review</button>
                <button onClick={() => setMenu(null)}>Pipeline completed successfully</button>
                <button onClick={() => setMenu(null)}>3 reports awaiting review</button>
            </>
          )}
          {menu === "profile" && (
            <>
              <b>Maya Riedel</b>
              <small>Portfolio Director</small>
              <button onClick={() => setMenu(null)}>Profile preferences</button>
              <button onClick={() => setMenu(null)}>Keyboard shortcuts</button>
            </>
          )}
        </div>
      )}
    </header>
  );
}
export function Button({
  children,
  secondary = false,
  onClick,
}: {
  children: React.ReactNode;
  secondary?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      className={`button ${secondary ? "secondary" : ""}`}
      onClick={onClick}
    >
      {children}
      <ArrowUpRight />
    </button>
  );
}
export function Modal({
  title,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <section
        className={`action-modal ${wide ? "wide" : ""}`}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <header>
          <div>
            <div className="eyebrow">PROJECTLENS WORKFLOW</div>
            <h2>{title}</h2>
          </div>
          <button onClick={onClose}>
            <X />
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </section>
    </div>
  );
}
export function Notice({
  message,
  onClose,
}: {
  message: string;
  onClose: () => void;
}) {
  return (
    <div className="notice">
      <CheckCircle2 />
      <span>{message}</span>
      <button onClick={onClose}>
        <X />
      </button>
    </div>
  );
}
