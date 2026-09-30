import {
  ArrowRight,
  CalendarClock,
  FileClock,
  Sparkles,
  TrendingDown,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button, Card, Kpi, PageHeader, StatusBadge } from "../components";
import { forecastData, money } from "../data";
import { useEffect, useState } from "react";
import { api } from "../services/api";

export function Overview({ onNavigate }: { onNavigate: (p: string) => void }) {
  const [projects, setProjects] = useState<any[]>([]);
  const [risks, setRisks] = useState<any[]>([]);
  useEffect(() => { api.projects().then(setProjects); api.risks().then(setRisks); }, []);
  const total = projects.reduce((a, p) => a + p.value, 0),
    exposure = projects.reduce((a, p) => a + p.riskExposure, 0),
    variance = projects.reduce((a, p) => a + p.variance, 0),
    margin = total ? projects.reduce((a,p)=>a+p.value*p.margin,0)/total : 0,
    delayed = projects.filter((p)=>p.scheduleDays>7).length;
  const health = [
    { name: "Healthy", value: projects.filter(p=>p.status==='Healthy').length, color: "#6f9c78" },
    { name: "Monitor", value: projects.filter(p=>p.status==='Monitor').length, color: "#c49a5a" },
    { name: "Attention", value: projects.filter(p=>p.status==='Attention').length, color: "#c6723f" },
    { name: "Critical", value: projects.filter(p=>p.status==='Critical').length, color: "#a95248" },
  ];
  return (
    <>
      <PageHeader
        title="Good morning, Maya."
        description="Here is what needs your attention across the portfolio today."
        actions={
          <>
            <button
              className="text-button"
              onClick={() => onNavigate("reports")}
            >
              View latest report
            </button>
            <Button onClick={() => onNavigate("assistant")}>
              <Sparkles /> Ask ProjectLens AI
            </Button>
          </>
        }
      />
      <div className="alert-strip">
        <div>
          <span>
            <TrendingDown />
          </span>
          <div>
            <b>Portfolio margin moved down 0.8 percentage points</b>
            <p>
              Driven primarily by Project Aurora and Project Nova in the
              September forecast.
            </p>
          </div>
        </div>
        <button onClick={() => onNavigate("forecasts")}>
          Investigate movement <ArrowRight />
        </button>
      </div>
      <div className="kpi-grid">
        <Kpi
          label="TOTAL PROJECT VALUE"
          value={money(total)}
          delta="+4.2%"
          detail="vs. last quarter"
        />
        <Kpi
          label="FORECAST COST VARIANCE"
          value={money(variance)}
          delta="Live"
          detail="portfolio variance"
          alert
        />
        <Kpi
          label="EXPECTED PORTFOLIO MARGIN"
          value={`${margin.toFixed(1)}%`}
          delta="Calculated"
          detail="weighted portfolio margin"
          alert
        />
        <Kpi
          label="OPEN RISK EXPOSURE"
          value={money(exposure)}
          delta="+8.4%"
          detail="month over month"
          alert
        />
        <Kpi
          label="PROJECTS REQUIRING ATTENTION"
          value={String(projects.filter(p=>['Attention','Critical'].includes(p.status)).length)}
          detail={`of ${projects.length} active projects`}
        />
        <Kpi
          label="DELAYED MILESTONES"
          value={String(delayed)}
          delta={`${projects.filter(p=>p.scheduleDays>20).length} critical`}
          detail="across portfolio"
          alert
        />
      </div>
      <div className="overview-grid">
        <Card
          title="Portfolio forecast trend"
          action={
            <button className="link" onClick={() => onNavigate("financials")}>
              Open financials <ArrowRight />
            </button>
          }
        >
          <div className="chart-meta">
            <span>
              <i className="dot bronze" /> Forecast cost
            </span>
            <span>
              <i className="dot grey" /> Budget
            </span>
            <b>
              €53.3M <small>current EAC</small>
            </b>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={forecastData}>
              <defs>
                <linearGradient id="bronzeArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stopColor="#b08d57" stopOpacity={0.38} />
                  <stop offset="1" stopColor="#b08d57" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#292724" vertical={false} />
              <XAxis
                dataKey="month"
                stroke="#78736d"
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={[48, 55]}
                stroke="#78736d"
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `€${v}M`}
              />
              <Tooltip
                contentStyle={{
                  background: "#171614",
                  border: "1px solid #4b4031",
                }}
              />
              <Area
                type="monotone"
                dataKey="forecast"
                stroke="#c49a5a"
                strokeWidth={2}
                fill="url(#bronzeArea)"
              />
              <Area
                type="monotone"
                dataKey="budget"
                stroke="#716d68"
                strokeDasharray="5 5"
                fill="none"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
        <Card
          title="Portfolio health"
          action={
            <button className="link" onClick={() => onNavigate("projects")}>
              All projects <ArrowRight />
            </button>
          }
        >
          <div className="donut-wrap">
            <ResponsiveContainer width="58%" height={200}>
              <PieChart>
                <Pie
                  data={health}
                  dataKey="value"
                  innerRadius={60}
                  outerRadius={82}
                  paddingAngle={3}
                >
                  {health.map((x) => (
                    <Cell key={x.name} fill={x.color} />
                  ))}
                </Pie>
                <text
                  x="50%"
                  y="45%"
                  textAnchor="middle"
                  fill="#f3eee6"
                  fontSize="28"
                  fontWeight="600"
                >
                  {projects.length}
                </text>
                <text
                  x="50%"
                  y="57%"
                  textAnchor="middle"
                  fill="#8b8781"
                  fontSize="11"
                >
                  PROJECTS
                </text>
              </PieChart>
            </ResponsiveContainer>
            <div className="legend">
              {health.map((x) => (
                <div key={x.name}>
                  <span>
                    <i style={{ background: x.color }} />
                    {x.name}
                  </span>
                  <b>{x.value}</b>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
      <Card
        title="Projects requiring attention"
        action={
          <button className="link" onClick={() => onNavigate("projects")}>
            View portfolio <ArrowRight />
          </button>
        }
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>PROJECT</th>
                <th>VALUE</th>
                <th>COMPLETION</th>
                <th>CURRENT MARGIN</th>
                <th>FORECAST VARIANCE</th>
                <th>SCHEDULE</th>
                <th>RISK EXPOSURE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {projects.slice().sort((a,b)=>b.riskExposure-a.riskExposure).slice(0,8).map((p) => (
                <tr key={p.id}>
                  <td>
                    <b>{p.name}</b>
                    <small>
                      {p.code} · {p.customer}
                    </small>
                  </td>
                  <td>{money(p.value)}</td>
                  <td>
                    <div className="progress-cell">
                      <span>
                        <i style={{ width: `${p.completion}%` }} />
                      </span>
                      {p.completion}%
                    </div>
                  </td>
                  <td className={p.margin < 12 ? "negative" : ""}>
                    {p.margin}%
                  </td>
                  <td className={p.variance > 0 ? "negative" : "positive"}>
                    {p.variance > 0 ? "+" : ""}
                    {money(p.variance)}
                  </td>
                  <td className={p.scheduleDays > 7 ? "negative" : ""}>
                    {p.scheduleDays ? `${p.scheduleDays}d late` : "On track"}
                  </td>
                  <td>{money(p.riskExposure)}</td>
                  <td>
                    <StatusBadge status={p.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <div className="lower-grid">
        <Card
          title="Priority risks"
          action={
            <button className="link" onClick={() => onNavigate("risks")}>
              Risk register <ArrowRight />
            </button>
          }
        >
          <div className="risk-list">
            {risks.slice(0, 3).map((r, i) => (
              <div key={r.id}>
                <span className={`risk-rank r${i}`}>{i + 1}</span>
                <div>
                  <b>{r.title}</b>
                  <small>
                    {projects.find((p) => p.id === r.project_id)?.name} ·{" "}
                    {r.category}
                  </small>
                </div>
                <strong>
                  {money(r.exposure)}
                  <small>EXPOSURE</small>
                </strong>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Upcoming actions">
          <div className="action-list">
            <div>
              <CalendarClock />
              <span>
                <b>Project Aurora — milestone recovery review</b>
                <small>Today · 14:00</small>
              </span>
            </div>
            <div>
              <FileClock />
              <span>
                <b>3 monthly reports awaiting approval</b>
                <small>Due tomorrow</small>
              </span>
            </div>
            <div>
              <Sparkles />
              <span>
                <b>Forecast commentary ready for review</b>
                <small>AI draft · September cycle</small>
              </span>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}
