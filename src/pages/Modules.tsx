import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  Check,
  CheckCircle2,
  CircleDashed,
  Clock,
  Database,
  FileSearch,
  Lightbulb,
  LockKeyhole,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Badge, Button, Card, Modal, Notice, PageHeader } from "../components";
import { money } from "../data";
import { api } from "../services/api";

const meta: Record<string, [string, string, string]> = {
  financials: [
    "FINANCIAL INTELLIGENCE",
    "Financial performance",
    "Filter and inspect verified portfolio financial records.",
  ],
  forecasts: [
    "FORECAST INTELLIGENCE",
    "Forecast movement",
    "Compare reporting cycles and review AI commentary.",
  ],
  risks: [
    "PORTFOLIO RISK",
    "Risk intelligence",
    "Inspect exposure and mitigation evidence.",
  ],
  contracts: [
    "CONTRACT INTELLIGENCE",
    "Contract search",
    "Ask live, clause-grounded contract questions.",
  ],
  knowledge: [
    "PROJECT KNOWLEDGE",
    "Knowledge library",
    "Browse and search connected project documents.",
  ],
  opportunities: [
    "TRANSFORMATION STUDIO",
    "AI Opportunities",
    "Assess business problems and choose the right solution.",
  ],
  reports: [
    "MANAGEMENT REPORTING",
    "Reports",
    "Generate and review database-backed PDF reports.",
  ],
  adoption: [
    "VALUE REALIZATION",
    "Adoption center",
    "Measure real usage and start role-based guidance.",
  ],
  governance: [
    "RESPONSIBLE AI",
    "Governance",
    "Inspect controls and audit history.",
  ],
  pipeline: [
    "DATA OPERATIONS",
    "Data pipeline",
    "Run and inspect transactional data processing.",
  ],
  settings: [
    "SYSTEM",
    "Settings",
    "Inspect live provider and workspace configuration.",
  ],
};
export function ModulePages({ page }: { page: string }) {
  const [eyebrow, title, description] = meta[page] || meta.financials;
  return (
    <>
      <PageHeader eyebrow={eyebrow} title={title} description={description} />
      {page === "financials" && <Financials />}
      {page === "forecasts" && <Forecasts />}
      {page === "risks" && <Risks />}
      {page === "contracts" && <Contracts />}
      {page === "knowledge" && <Knowledge />}
      {page === "opportunities" && <Opportunities />}
      {page === "reports" && <Reports />}
      {page === "adoption" && <Adoption />}
      {page === "governance" && <Governance />}
      {page === "pipeline" && <Pipeline />}
      {page === "settings" && <Settings />}
    </>
  );
}

function Financials() {
  const [projects, setProjects] = useState<any[]>([]),
    [selected, setSelected] = useState("all"),
    [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    api.projects().then(setProjects);
    api.financials().then(setRows);
  }, []);
  const visible =
    selected === "all" ? rows : rows.filter((x) => x.project_id === selected);
  const latest = Object.values(
    visible.reduce((a: any, x: any) => {
      if (!a[x.project_id] || a[x.project_id].period < x.period)
        a[x.project_id] = x;
      return a;
    }, {}),
  ) as any[];
  const budget = latest.reduce((a, x) => a + x.budget, 0),
    forecast = latest.reduce((a, x) => a + x.forecast_cost, 0),
    revenue = latest.reduce((a, x) => a + x.forecast_revenue, 0);
  return (
    <>
      <div className="module-toolbar">
        <select value={selected} onChange={(e) => setSelected(e.target.value)}>
          <option value="all">All projects</option>
          {projects.map((p) => (
            <option value={p.id}>{p.name}</option>
          ))}
        </select>
        <span>{visible.length} financial records</span>
      </div>
      <div className="kpi-grid four">
        <Metric l="PLANNED COST" v={money(budget)} s="Latest baselines" />
        <Metric
          l="FORECAST COST"
          v={money(forecast)}
          s={`${money(forecast - budget)} variance`}
          bad={forecast > budget}
        />
        <Metric
          l="FORECAST REVENUE"
          v={money(revenue)}
          s="Verified project records"
        />
        <Metric
          l="EXPECTED MARGIN"
          v={`${revenue ? (((revenue - forecast) / revenue) * 100).toFixed(1) : 0}%`}
          s="Calculated, not generated"
        />
      </div>
      <Card title="Current project financial position">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart
            data={latest.slice(0, 12).map((x) => ({
              name:
                projects
                  .find((p) => p.id === x.project_id)
                  ?.name?.replace("Project ", "") || "Project",
              budget: x.budget / 1e6,
              forecast: x.forecast_cost / 1e6,
            }))}
          >
            <CartesianGrid stroke="#292724" vertical={false} />
            <XAxis dataKey="name" stroke="#77716a" />
            <YAxis stroke="#77716a" tickFormatter={(v) => `€${v}M`} />
            <Tooltip
              contentStyle={{
                background: "#171614",
                border: "1px solid #4b4031",
              }}
            />
            <Bar dataKey="budget" fill="#5e554a" />
            <Bar dataKey="forecast" fill="#b08d57" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </>
  );
}

function Forecasts() {
  const [allProjects, setAllProjects] = useState<any[]>([]),
    [project, setProject] = useState<any>(null),
    [versions, setVersions] = useState<any[]>([]),
    [review, setReview] = useState("Draft"),
    [editing, setEditing] = useState(false),
    [text, setText] = useState(
      "Supplier recovery actions are the primary cost driver.",
    );
  useEffect(() => {
    api.projects().then((p) => {
      setAllProjects(p);
      setProject(p[0]);
      api.forecasts(p[0].id).then(setVersions);
    });
  }, []);
  const previous = versions[0],
    current = versions[1],
    drivers = current ? Object.entries(current.drivers) : [];
  return (
    <>
      {review !== "Draft" && (
        <Notice
          message={`Forecast commentary marked ${review}`}
          onClose={() => setReview("Draft")}
        />
      )}
      <div className="module-toolbar">
        <select
          value={project?.id || ""}
          onChange={async (e) => {
            const p = allProjects.find((x) => x.id === e.target.value);
            setProject(p);
            setVersions(await api.forecasts(p.id));
          }}
        >
          {allProjects.map((p) => (
            <option value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>
      <div className="split">
        <Card title="Forecast comparison">
          <div className="forecast-summary">
            <div>
              <small>PREVIOUS</small>
              <b>{money(previous?.total_cost || 0)}</b>
            </div>
            <ArrowRight />
            <div>
              <small>CURRENT</small>
              <b>{money(current?.total_cost || 0)}</b>
            </div>
            <Badge tone="red">
              {money((current?.total_cost || 0) - (previous?.total_cost || 0))}
            </Badge>
          </div>
          <div className="driver-list">
            {drivers.map(([n, v]) => (
              <div>
                <span>{n}</span>
                <i>
                  <em
                    style={{
                      width: `${Math.min(100, (Math.abs(Number(v)) / Math.max(...drivers.map((x) => Math.abs(Number(x[1]))))) * 100)}%`,
                    }}
                  />
                </i>
                <b className={Number(v) > 0 ? "negative" : "positive"}>
                  {money(Number(v))}
                </b>
              </div>
            ))}
          </div>
        </Card>
        <Card title="AI commentary">
          <div className="insight-box">
            <span>AI GENERATED · {review.toUpperCase()}</span>
            {editing ? (
              <textarea
                className="editor"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            ) : (
              <>
                <h3>{text}</h3>
                <p>
                  Commentary uses stored forecast versions and requires human
                  review.
                </p>
              </>
            )}
            <small>Sources: Forecast v8 and v9</small>
          </div>
          <div className="review-buttons">
            <button onClick={() => setReview("Rejected")}>Reject</button>
            <button onClick={() => setEditing(!editing)}>
              {editing ? "Save" : "Edit"}
            </button>
            <button className="approve" onClick={() => setReview("Approved")}>
              <Check /> Approve
            </button>
          </div>
        </Card>
      </div>
    </>
  );
}

function Risks() {
  const [rows, setRows] = useState<any[]>([]),
    [selected, setSelected] = useState<any>(null);
  useEffect(() => {
    api.risks().then(setRows);
  }, []);
  return (
    <>
      <Card title="Risk register">
        <table>
          <thead>
            <tr>
              <th>RISK</th>
              <th>CATEGORY</th>
              <th>PROBABILITY</th>
              <th>IMPACT</th>
              <th>EXPOSURE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr className="clickable" onClick={() => setSelected(r)}>
                <td>
                  <b>{r.title}</b>
                  <small>
                    {r.id} · {r.owner}
                  </small>
                </td>
                <td>
                  <Badge>{r.category}</Badge>
                </td>
                <td>{Math.round(r.probability * 100)}%</td>
                <td>{money(r.impact)}</td>
                <td>
                  <b>{money(r.exposure)}</b>
                </td>
                <td>
                  <Badge tone="bronze">{r.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      {selected && (
        <Modal title={selected.title} onClose={() => setSelected(null)}>
          <div className="detail-grid">
            <Detail l="Risk ID" v={selected.id} />
            <Detail l="Exposure" v={money(selected.exposure)} />
            <Detail l="Owner" v={selected.owner} />
            <Detail l="Status" v={selected.status} />
          </div>
          <h3>Mitigation</h3>
          <p>{selected.mitigation}</p>
        </Modal>
      )}
    </>
  );
}

function Contracts() {
  const suggestedQuestions = [
    "What are the payment milestones and invoice payment period?",
    "What is the contractual delivery date and what completes delivery?",
    "What liquidated damages apply to delay and what is the cap?",
    "How long is the warranty period and when does it start?",
    "What conditions must be met for provisional and final acceptance?",
    "How must a contract change be submitted and approved?",
    "What information and notice period are required for a claim?",
    "What are the termination rights for breach and convenience?",
    "What liability cap and exclusions apply under the contract?",
    "How are disputes escalated and finally resolved?",
  ];
  const [q, setQ] = useState("What are the payment terms for Project Atlas?"),
    [answer, setAnswer] = useState<any>(null),
    [loading, setLoading] = useState(false),
    [contracts, setContracts] = useState<any[]>([]),
    [selected, setSelected] = useState<any>(null),
    [page, setPage] = useState(1),
    [error, setError] = useState("");
  useEffect(() => { api.contracts().then((rows) => { setContracts(rows); setSelected(rows[0]); }); }, []);
  const ask = async () => {
    setLoading(true); setError("");
    try {
      setAnswer(await api.query(q, selected?.project_id, selected?.id));
    } catch (e: any) {
      setAnswer(null); setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  const clearChat = () => { setQ(""); setAnswer(null); setError(""); setPage(1); };
  return (
    <div className="contract-workbench">
      <Card title="Contract portfolio">
        <select value={selected?.id || ""} onChange={(e) => { setSelected(contracts.find(c => c.id === e.target.value)); setPage(1); setAnswer(null); }}>
          {contracts.map(c => <option key={c.id} value={c.id}>{c.contract_number} · {c.name}</option>)}
        </select>
        {selected && <div className="detail-grid"><Detail l="Customer" v={selected.customer}/><Detail l="Value" v={money(selected.value)}/><Detail l="Pages" v={selected.page_count}/><Detail l="Index" v={selected.ingestion_status}/></div>}
        <div className="review-buttons"><a className="approve" href={selected ? api.contractPdf(selected.id, true) : "#"}>Download PDF</a><button onClick={async()=>selected && await api.reindexContract(selected.id)}><RefreshCw/> Re-index</button></div>
      </Card>
      <Card title={`Source document · page ${page}`}>
        {selected && <iframe title="Contract PDF" className="contract-pdf" src={`${api.contractPdf(selected.id)}#page=${page}&view=FitH`} />}
      </Card>
      <Card>
        <div className="search-hero">
          <FileSearch />
          <h2>Ask the contract portfolio</h2>
          <p>Every answer is grounded in stored contract clauses.</p>
          <select value="" onChange={(e) => setQ(e.target.value)} aria-label="Suggested contract questions">
            <option value="">Choose one of 10 suggested questions…</option>
            {suggestedQuestions.map((question)=><option key={question} value={question}>{question}</option>)}
          </select>
          <div>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask()}
            />
            <button disabled={loading} onClick={ask}>
              <Sparkles /> {loading ? "Searching…" : "Ask"}
            </button>
          </div>
          <button className="clear-chat" type="button" onClick={clearChat}>Clear question and answer</button>
        </div>
        {error && <p className="negative">{error}</p>}
        {answer ? (
          <>
            <Badge tone="bronze">{answer.pipeline}</Badge>
            <h3>{answer.summary}</h3>
            {answer.sources.map((s: any) => (
              <button className="citation" onClick={() => setPage(s.page)}>
                <FileSearch />
                <span>
                  <b>
                    {s.title} · {s.section}
                  </b>
                  <small>
                    Page {s.page} · Chunk {s.id}
                  </small>
                </span>
                <ShieldCheck />
              </button>
            ))}
            <small className="support-note">
              {answer.sources.length} validated sources ·{" "}
              {Math.round(answer.confidence * 100)}% confidence
            </small>
          </>
        ) : (
          <div className="empty-state">
            Ask a contract question to retrieve verified clauses.
          </div>
        )}
      </Card>
    </div>
  );
}

const docTypes = [
  ["meeting_note", "Meeting notes"],
  ["monthly_report", "Monthly reports"],
  ["lesson_learned", "Lessons learned"],
  ["project_update", "Project updates"],
];
function Knowledge() {
  const [docs, setDocs] = useState<any[]>([]),
    [type, setType] = useState<string | null>(null),
    [selected, setSelected] = useState<any>(null);
  useEffect(() => {
    api.documents().then(setDocs);
  }, []);
  return (
    <>
      <div className="document-grid">
        {docTypes.map(([key, title]) => (
          <Card key={key}>
            <Database />
            <b>{docs.filter((d) => d.document_type === key).length}</b>
            <h3>{title}</h3>
            <p>Connected, searchable project evidence.</p>
            <button onClick={() => setType(key)}>
              Browse library <ArrowRight />
            </button>
          </Card>
        ))}
      </div>
      {type && (
        <Modal
          wide
          title={docTypes.find((x) => x[0] === type)?.[1] || "Documents"}
          onClose={() => setType(null)}
        >
          <div className="library-list">
            {docs
              .filter((d) => d.document_type === type)
              .map((d) => (
                <button onClick={() => setSelected(d)}>
                  <b>{d.title}</b>
                  <small>
                    {d.section} · Page {d.page}
                  </small>
                </button>
              ))}
          </div>
        </Modal>
      )}
      {selected && (
        <Modal title={selected.title} onClose={() => setSelected(null)}>
          <Badge>{selected.document_type}</Badge>
          <p className="document-content">{selected.content}</p>
        </Modal>
      )}
    </>
  );
}

function Opportunities() {
  const stages = ["Idea", "Assessment", "Prototype", "Testing", "Pilot", "Ready", "Rejected"];
  const [items, setItems] = useState<any[]>([]),
    [open, setOpen] = useState(false),
    [result, setResult] = useState<any>(null),
    [reviewComment, setReviewComment] = useState("Assessment reviewed against business value, data readiness, security, and human oversight requirements."),
    [dragged, setDragged] = useState<any>(null),
    [pendingStage, setPendingStage] = useState(""),
    [stageComment, setStageComment] = useState("Stage changed after human review of the required evidence."),
    [notice, setNotice] = useState(""),
    [form, setForm] = useState({
      title: "",
      business_problem: "",
      current_process: "",
      owner: "Maya Riedel",
    });
  const load = () => void api.useCases().then(setItems);
  useEffect(() => load(), []);
  const create = async () => {
    const x = await api.createUseCase(form);
    setOpen(false);
    setResult(x);
    load();
  };
  const review = async (decision: string) => {
    const updated = await api.reviewUseCase(result.id, decision, reviewComment);
    setResult(updated); setNotice(decision === "approve" ? "Opportunity approved and moved to Prototype" : decision === "reject" ? "Opportunity rejected" : "Changes requested; opportunity remains in Assessment"); load();
  };
  const moveStage = async () => {
    if (!result || !pendingStage) return;
    const updated = await api.changeUseCaseStage(result.id, pendingStage, stageComment);
    setResult(updated); setPendingStage(""); setNotice(`Opportunity moved to ${updated.status}`); load();
  };
  const remove = async () => {
    if (!result || !window.confirm(`Delete “${result.title}”? This cannot be undone.`)) return;
    const title=result.title; await api.deleteUseCase(result.id); setResult(null); setNotice(`${title} deleted`); load();
  };
  return (
    <>
      {notice && <Notice message={notice} onClose={() => setNotice("")} />}
      <div className="studio-callout">
        <Lightbulb />
        <div>
          <b>Start with the business problem, not the technology.</b>
          <p>
            The assessment may explicitly determine that AI is not required.
          </p>
        </div>
        <Button onClick={() => setOpen(true)}>New assessment</Button>
      </div>
      <div className="kanban">
        {stages.map(
          (c) => (
            <div onDragOver={(e)=>e.preventDefault()} onDrop={()=>{ if(dragged && dragged.status!==c){ setResult(dragged); setPendingStage(c); } setDragged(null); }}>
              <header>
                <span>{c}</span>
                <b>{items.filter((x) => x.status === c).length}</b>
              </header>
              {items
                .filter((x) => x.status === c)
                .map((x) => (
                  <article draggable onDragStart={()=>setDragged(x)} onDragEnd={()=>setDragged(null)} onClick={() => setResult(x)}>
                    <Badge>
                      {x.assessment?.ai_needed ? "AI" : "AUTOMATION"}
                    </Badge>
                    <h4>{x.title}</h4>
                    <p>{x.business_problem}</p>
                    <small>
                      {x.assessment?.ai_needed
                        ? "Human review required"
                        : "AI NOT REQUIRED"}
                    </small>
                  </article>
                ))}
            </div>
          ),
        )}
      </div>
      {open && (
        <Modal title="Assess an AI opportunity" onClose={() => setOpen(false)}>
          <div className="form-grid">
            <label>
              Title
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </label>
            <label>
              Business problem
              <textarea
                value={form.business_problem}
                onChange={(e) =>
                  setForm({ ...form, business_problem: e.target.value })
                }
              />
            </label>
            <label>
              Current process
              <textarea
                value={form.current_process}
                onChange={(e) =>
                  setForm({ ...form, current_process: e.target.value })
                }
              />
            </label>
            <label>
              Owner
              <input
                value={form.owner}
                onChange={(e) => setForm({ ...form, owner: e.target.value })}
              />
            </label>
          </div>
          <Button onClick={create}>Run assessment</Button>
        </Modal>
      )}
      {result && (
        <Modal title={result.title} onClose={() => setResult(null)}>
          <h3>Recommended approach</h3>
          <p>
            {result.assessment?.recommended_approach || "Existing assessment"}
          </p>
          <div className="detail-grid">
            <Detail
              l="AI needed"
              v={result.assessment?.ai_needed ? "Yes" : "No"}
            />
            <Detail
              l="Automation"
              v={result.assessment?.automation_needed ? "Yes" : "No"}
            />
            <Detail l="RAG" v={result.assessment?.rag_needed ? "Yes" : "No"} />
            <Detail l="Status" v={result.status} />
            <Detail l="Complexity" v={result.assessment?.complexity || "Not assessed"} />
            <Detail l="Human review" v={result.assessment?.human_review_required ? "Required" : "Not required"} />
            <Detail l="Assessed by" v={result.assessment?.assessment_provider || "Legacy assessment"} />
          </div>
          {result.assessment?.rationale && <><h3>Assessment rationale</h3><ul>{result.assessment.rationale.map((x:string)=><li key={x}>{x}</li>)}</ul></>}
          {result.assessment?.security_considerations && <><h3>Security considerations</h3><ul>{result.assessment.security_considerations.map((x:string)=><li key={x}>{x}</li>)}</ul></>}
          {result.assessment?.human_review && <Notice message={`${result.assessment.human_review.reviewer}: ${result.assessment.human_review.comments}`} onClose={()=>{}} />}
          {result.status === "Assessment" && <><h3>Human review decision</h3><textarea className="editor" value={reviewComment} onChange={(e)=>setReviewComment(e.target.value)} /><div className="review-buttons"><button onClick={()=>review("reject")}>Reject</button><button onClick={()=>review("request_changes")}>Request changes</button><button className="approve" onClick={()=>review("approve")}><Check/> Approve for prototype</button></div></>}
          <h3>Change stage</h3>
          <select value={pendingStage} onChange={(e)=>setPendingStage(e.target.value)}><option value="">Select destination</option>{stages.filter(s=>s!==result.status).map(s=><option key={s} value={s}>{s}</option>)}</select>
          {pendingStage && <><textarea className="editor" value={stageComment} onChange={(e)=>setStageComment(e.target.value)} /><div className="review-buttons"><button onClick={()=>setPendingStage("")}>Cancel</button><button className="approve" onClick={moveStage}>Save comment and move</button></div></>}
          {result.assessment?.stage_history?.length > 0 && <><h3>Stage history</h3><div className="library-list">{[...result.assessment.stage_history].reverse().map((h:any,i:number)=><div key={i}><b>{h.from} → {h.to}</b><small>{h.changed_by} · {new Date(h.changed_at).toLocaleString()}</small><p>{h.comments}</p></div>)}</div></>}
          <div className="danger-zone"><div><b>Delete opportunity</b><small>Remove this card while retaining an audit record.</small></div><button onClick={remove}>Delete card</button></div>
        </Modal>
      )}
    </>
  );
}

function Reports() {
  const [rows, setRows] = useState<any[]>([]),
    [projects, setProjects] = useState<any[]>([]),
    [selectedProject, setSelectedProject] = useState(""),
    [selected, setSelected] = useState<any>(null),
    [notice, setNotice] = useState("");
  const load = () => api.reports().then(setRows);
  useEffect(() => {
    load();
    api.projects().then((x) => {
      setProjects(x);
      setSelectedProject(x[0]?.id);
    });
  }, []);
  const generate = async () => {
    const x = await api.generateReport(selectedProject);
    setNotice("Monthly project review generated as Draft");
    setSelected(x);
    load();
  };
  const review = async (status: string) => {
    await api.reviewReport(selected.id, status);
    setNotice(`Report marked ${status}`);
    setSelected({ ...selected, status });
    load();
  };
  return (
    <>
      {notice && <Notice message={notice} onClose={() => setNotice("")} />}
      <div className="module-toolbar">
        <select
          value={selectedProject}
          onChange={(e) => setSelectedProject(e.target.value)}
        >
          {projects.map((p) => (
            <option value={p.id}>{p.name}</option>
          ))}
        </select>
        <Button onClick={generate}>
          <Sparkles /> Generate report
        </Button>
      </div>
      <div className="report-grid">
        {rows.map((r) => (
          <Card key={r.id}>
            <div className="report-icon">
              <FileSearch />
            </div>
            <Badge tone={r.status === "Approved" ? "green" : "bronze"}>
              {r.status}
            </Badge>
            <h3>{r.report_type}</h3>
            <p>{r.period}</p>
            <button onClick={() => setSelected(r)}>
              Open report <ArrowRight />
            </button>
          </Card>
        ))}
      </div>
      {selected && (
        <Modal
          wide
          title={
            selected.content?.title ||
            selected.report_type ||
            "Generated report"
          }
          onClose={() => setSelected(null)}
        >
          <Badge>{selected.status}</Badge>
          <p>{selected.content?.executive_summary}</p>
          <pre className="report-json">
            {JSON.stringify(selected.content, null, 2)}
          </pre>
          <div className="review-buttons">
            <a className="approve" href={api.reportDownload(selected.id,"pdf")}>Download PDF</a>
            <a href={api.reportDownload(selected.id,"xlsx")}>Download XLSX</a>
          </div>
          <div className="review-buttons">
            <button onClick={() => review("Rejected")}>Reject</button>
            <button onClick={() => review("Reviewed")}>Mark reviewed</button>
            <button className="approve" onClick={() => review("Approved")}>
              <Check /> Approve
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}

function Adoption() {
  const [data, setData] = useState<any>({}),
    [guide, setGuide] = useState<string | null>(null);
  useEffect(() => {
    api.adoption().then(setData);
  }, []);
  const guides = [
    "Getting started",
    "Using contract search",
    "Reviewing AI output",
    "Generating reports",
    "Providing feedback",
  ];
  return (
    <>
      <div className="kpi-grid four">
        <Metric
          l="ACTIVE USERS"
          v={String(data.active_users ?? 0)}
          s="Authenticated accounts"
        />
        <Metric
          l="AI QUESTIONS"
          v={String(data.ai_questions ?? 0)}
          s="Stored AI runs"
        />
        <Metric
          l="USEFUL ANSWERS"
          v={`${data.satisfaction_score ?? 0}%`}
          s={`${data.feedback_count ?? 0} ratings`}
        />
        <Metric
          l="CITATION COVERAGE"
          v={`${data.citation_coverage ?? 100}%`}
          s="Auditable outputs"
        />
      </div>
      <div className="training-grid">
        {guides.map((x, i) => (
          <Card>
            <span>0{i + 1}</span>
            <h3>{x}</h3>
            <p>Interactive guidance for this workflow.</p>
            <button onClick={() => setGuide(x)}>
              Start guide <ArrowRight />
            </button>
          </Card>
        ))}
      </div>
      {guide && (
        <Modal title={guide} onClose={() => setGuide(null)}>
          <ol className="guide">
            <li>Open the relevant module from the left navigation.</li>
            <li>Select a project or enter a grounded question.</li>
            <li>Review calculated facts and cited evidence.</li>
            <li>Approve, reject, or provide feedback where required.</li>
          </ol>
          <Button onClick={() => setGuide(null)}>Complete guide</Button>
        </Modal>
      )}
    </>
  );
}

function Governance() {
  const [data, setData] = useState<any>(null),
    [audit, setAudit] = useState<any[]>([]),
    [show, setShow] = useState(false);
  useEffect(() => {
    api.governance().then(setData);
    api.audit().then(setAudit);
  }, []);
  return (
    <>
      <div className="principles">
        <ShieldCheck />
        <div>
          <b>Decision support, with accountable humans in control.</b>
          <p>{data?.principles?.join(" · ")}</p>
        </div>
        <Button onClick={() => setShow(true)}>View audit log</Button>
      </div>
      <Card title="Provider controls">
        <table>
          <thead>
            <tr>
              <th>PROVIDER</th>
              <th>STATUS</th>
              <th>IMPLEMENTED</th>
              <th>TRACEABILITY</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <b>Gemini</b>
              </td>
              <td>
                <Badge tone="green">Active</Badge>
              </td>
              <td>Yes</td>
              <td>Model, prompt, sources, output</td>
            </tr>
            <tr>
              <td>
                <b>Private AI</b>
              </td>
              <td>
                <Badge>Future option</Badge>
              </td>
              <td>No</td>
              <td>Provider interface only</td>
            </tr>
          </tbody>
        </table>
      </Card>
      {show && (
        <Modal wide title="Audit log" onClose={() => setShow(false)}>
          <table>
            <thead>
              <tr>
                <th>TIME</th>
                <th>ACTION</th>
                <th>ENTITY</th>
                <th>DETAILS</th>
              </tr>
            </thead>
            <tbody>
              {audit.map((x) => (
                <tr>
                  <td>{new Date(x.timestamp).toLocaleString()}</td>
                  <td>{x.action}</td>
                  <td>{x.entity_type}</td>
                  <td>{JSON.stringify(x.details)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Modal>
      )}
    </>
  );
}

function Pipeline() {
  const [run, setRun] = useState<any>(null),
    [running, setRunning] = useState(false),
    [history, setHistory] = useState<any[]>([]);
  const load = () => void api.pipelines().then(setHistory);
  useEffect(() => load(), []);
  const execute = async () => {
    setRunning(true);
    try {
      const x = await api.runPipeline();
      setRun(x);
      load();
    } finally {
      setRunning(false);
    }
  };
  const latest = run || history[0];
  return (
    <>
      <div className="module-toolbar">
        <span>
          {latest ? `Last run: ${latest.status}` : "No pipeline run recorded"}
        </span>
        <Button onClick={execute}>
          <Play /> {running ? "Running…" : "Run pipeline"}
        </Button>
      </div>
      {latest && (
        <div className="pipeline-summary">
          <div>
            <CheckCircle2 />
            <span>
              <b>{latest.status}</b>
              <small>{latest.id}</small>
            </span>
          </div>
          <div>
            <b>{latest.records_processed}</b>
            <small>PROCESSED</small>
          </div>
          <div>
            <b>{latest.inserted}</b>
            <small>INSERTED</small>
          </div>
          <div>
            <b>{latest.updated}</b>
            <small>UPDATED</small>
          </div>
          <div>
            <b>{latest.failed}</b>
            <small>FAILED</small>
          </div>
          <button onClick={execute}>
            <RefreshCw /> Run again
          </button>
        </div>
      )}
      <Card title="Pipeline execution">
        <div className="pipeline">
          {(
            latest?.steps ||
            [
              "Import",
              "Validation",
              "Cleaning",
              "Transformation",
              "Deduplication",
              "Financial calculations",
              "Risk calculations",
              "Document processing",
              "Embeddings",
              "Database commit",
            ].map((name) => ({ name, status: "Pending" }))
          ).map((s: any) => (
            <div>
              <span className={s.status === "Successful" ? "done" : "current"}>
                {s.status === "Successful" ? <Check /> : <CircleDashed />}
              </span>
              <div>
                <b>{s.name}</b>
                <small>{s.status}</small>
              </div>
              <Badge tone={s.status === "Successful" ? "green" : "neutral"}>
                {s.status.toUpperCase()}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}

function Settings() {
  const [notice, setNotice] = useState("");
  return (
    <>
      {notice && <Notice message={notice} onClose={() => setNotice("")} />}
      <div className="settings-grid">
        <Card>
          <div className="provider-head">
            <Bot />
            <Badge tone="green">ACTIVE</Badge>
          </div>
          <h2>Cloud AI</h2>
          <h3>Gemini</h3>
          <p>Live provider is configured through the server environment.</p>
          <ul>
            <li>
              <Check /> Structured JSON
            </li>
            <li>
              <Check /> Versioned prompts
            </li>
            <li>
              <Check /> Validated sources
            </li>
          </ul>
          <Button
            onClick={async () => {
              const r = await api.query(
                "Return a concise portfolio status check.",
              );
              setNotice(
                `Gemini verified: ${Math.round(r.confidence * 100)}% confidence`,
              );
            }}
          >
            Test connection
          </Button>
        </Card>
        <Card>
          <div className="provider-head muted">
            <Database />
            <Badge>FUTURE OPTION</Badge>
          </div>
          <h2>Private AI deployment</h2>
          <p>No local model is implemented.</p>
          <Button
            secondary
            onClick={() =>
              setNotice(
                "Private provider architecture documented; execution remains intentionally disabled.",
              )
            }
          >
            View readiness
          </Button>
        </Card>
      </div>
    </>
  );
}

function Metric({
  l,
  v,
  s,
  bad = false,
}: {
  l: string;
  v: string;
  s: string;
  bad?: boolean;
}) {
  return (
    <Card className="kpi">
      <div className="kpi-label">{l}</div>
      <div className="kpi-value">{v}</div>
      <div className={`kpi-detail ${bad ? "negative" : ""}`}>{s}</div>
    </Card>
  );
}
function Detail({ l, v }: { l: string; v: string }) {
  return (
    <div>
      <small>{l}</small>
      <b>{v}</b>
    </div>
  );
}
