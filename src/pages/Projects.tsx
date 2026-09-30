import { Filter, Search, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, Modal, PageHeader, StatusBadge } from "../components";
import { money } from "../data";
import { api } from "../services/api";

export function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]),
    [selected, setSelected] = useState<any>(null),
    [workspace, setWorkspace] = useState<any>(null),
    [q, setQ] = useState(""),
    [region, setRegion] = useState("All"),
    [status, setStatus] = useState("All"),
    [config, setConfig] = useState(false),
    [showRisk, setShowRisk] = useState(true);
  useEffect(() => {
    api.projects().then((x) => {
      setProjects(x);
      setSelected(x[0]);
    });
  }, []);
  useEffect(() => {
    if (selected) api.projectWorkspace(selected.id).then(setWorkspace);
  }, [selected]);
  const filtered = useMemo(
    () =>
      projects.filter(
        (p) =>
          (region === "All" || p.region === region) &&
          (status === "All" || p.status === status) &&
          `${p.name} ${p.code} ${p.customer}`
            .toLowerCase()
            .includes(q.toLowerCase()),
      ),
    [projects, q, region, status],
  );
  return (
    <>
      <PageHeader
        eyebrow="PORTFOLIO / PROJECTS"
        title="Projects"
        description="Database-backed project performance, delivery, and exposure."
        actions={
          <button className="button secondary" onClick={() => setConfig(true)}>
            <SlidersHorizontal /> Configure view
          </button>
        }
      />
      <div className="filters">
        <div>
          <Search />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search projects…"
          />
        </div>
        <label>
          <Filter />
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option>All</option>
            {[...new Set(projects.map((p) => p.region))].map((x) => (
              <option>{x}</option>
            ))}
          </select>
        </label>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option>All</option>
          {["Healthy", "Monitor", "Attention", "Critical"].map((x) => (
            <option>{x}</option>
          ))}
        </select>
        <span>{filtered.length} projects</span>
      </div>
      <div className="project-layout">
        <Card className="project-list">
          <div className="project-cards">
            {filtered.map((p) => (
              <button
                className={selected?.id === p.id ? "selected" : ""}
                onClick={() => setSelected(p)}
                key={p.id}
              >
                <div>
                  <b>{p.name}</b>
                  <small>
                    {p.code} · {p.region}
                  </small>
                </div>
                <StatusBadge status={p.status} />
                <div className="mini-metrics">
                  <span>
                    VALUE <b>{money(p.value)}</b>
                  </span>
                  <span>
                    COMPLETE <b>{p.completion}%</b>
                  </span>
                  <span>
                    MARGIN <b>{p.margin.toFixed(1)}%</b>
                  </span>
                </div>
              </button>
            ))}
          </div>
        </Card>
        {selected && (
          <div className="project-detail">
            <div className="detail-title">
              <div>
                <span>{selected.code}</span>
                <h2>{selected.name}</h2>
                <p>
                  {selected.customer} · {selected.region}
                </p>
              </div>
              <StatusBadge status={selected.status} />
            </div>
            <div className="detail-kpis">
              <div>
                <small>PROJECT VALUE</small>
                <b>{money(selected.value)}</b>
              </div>
              <div>
                <small>COMPLETION</small>
                <b>{selected.completion}%</b>
              </div>
              <div>
                <small>EXPECTED MARGIN</small>
                <b>{selected.margin.toFixed(1)}%</b>
              </div>
              {showRisk && (
                <div>
                  <small>RISK EXPOSURE</small>
                  <b>{money(selected.riskExposure)}</b>
                </div>
              )}
            </div>
            <Card title="Financial trajectory">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={(workspace?.financials || [])
                    .slice(-8)
                    .map((x: any) => ({
                      n: x.period,
                      actual: x.actual_cost / 1e6,
                      forecast: x.forecast_cost / 1e6,
                    }))}
                >
                  <CartesianGrid stroke="#292724" vertical={false} />
                  <XAxis dataKey="n" stroke="#77716a" />
                  <YAxis stroke="#77716a" tickFormatter={(v) => `€${v}M`} />
                  <Tooltip
                    contentStyle={{
                      background: "#171614",
                      border: "1px solid #4b4031",
                    }}
                  />
                  <Bar dataKey="actual" fill="#5e554a" />
                  <Bar dataKey="forecast" fill="#b08d57" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            <div className="project-tabs">
              <Card title="Milestones">
                <div className="compact-list">
                  {workspace?.milestones?.map((x: any) => (
                    <div>
                      <span>
                        <b>{x.name}</b>
                        <small>{x.forecast_date}</small>
                      </span>
                      <StatusBadge status={x.status} />
                    </div>
                  ))}
                </div>
              </Card>
              <Card title="Documents & changes">
                <div className="compact-list">
                  <div>
                    <span>
                      <b>Knowledge documents</b>
                      <small>Meeting notes, reports, lessons, updates</small>
                    </span>
                    <strong>{workspace?.documents?.length || 0}</strong>
                  </div>
                  <div>
                    <span>
                      <b>Change orders</b>
                      <small>Linked commercial changes</small>
                    </span>
                    <strong>{workspace?.change_orders?.length || 0}</strong>
                  </div>
                  <div>
                    <span>
                      <b>Open risks</b>
                      <small>With mitigation evidence</small>
                    </span>
                    <strong>{workspace?.risks?.length || 0}</strong>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
      {config && (
        <Modal title="Configure project view" onClose={() => setConfig(false)}>
          <label className="check-row">
            <input
              type="checkbox"
              checked={showRisk}
              onChange={(e) => setShowRisk(e.target.checked)}
            />{" "}
            Show risk exposure KPI
          </label>
          <p>
            Search, region, and status filters are available directly above the
            project list.
          </p>
          <button className="button" onClick={() => setConfig(false)}>
            Apply view
          </button>
        </Modal>
      )}
    </>
  );
}
