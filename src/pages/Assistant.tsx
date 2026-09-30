import {
  BookOpen,
  Database,
  FileText,
  LoaderCircle,
  Send,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { useState } from "react";
import { Badge, Card, Modal, Notice, PageHeader } from "../components";
import { api } from "../services/api";

const suggestions = [
  "Which projects need attention?",
  "Why did Project Aurora’s margin fall?",
  "What are the payment terms for Project Atlas?",
  "What lessons have we learned from supplier delays?",
];
type Message = {
  q: string;
  a: string;
  type: string;
  sources: string[];
  confidence: number;
  runId?: string;
};
export function Assistant() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [source, setSource] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const ask = async (text = q) => {
    if (!text.trim() || loading) return;
    setQ("");
    setLoading(true);
    try {
      const r = await api.query(text);
      setMessages((m) => [
        ...m,
        {
          q: text,
          a: r.summary,
          type: String(r.pipeline).replaceAll("_", " ").toUpperCase(),
          sources: r.sources.map(
            (s: any) =>
              `${s.title} · ${s.section || "Verified source"}${s.page ? ` · Page ${s.page}` : ""}`,
          ),
          confidence: r.confidence,
          runId: r.run_id,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          q: text,
          a: e instanceof Error ? e.message : "The assistant is unavailable.",
          type: "SYSTEM",
          sources: [],
          confidence: 0,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      {notice && <Notice message={notice} onClose={() => setNotice("")} />}
      <PageHeader
        eyebrow="PROJECTLENS / AI ASSISTANT"
        title="Ask across your project portfolio"
        description="Live Gemini answers routed to verified analytics, contracts, or project knowledge."
      />
      <div className="assistant-layout">
        <aside className="assistant-side">
          <h3>Suggested questions</h3>
          {suggestions.map((s) => (
            <button key={s} onClick={() => ask(s)}>
              {s}
            </button>
          ))}
          <Card>
            <ShieldCheck />
            <b>Grounded by design</b>
            <p>
              Gemini receives only retrieved evidence. Unsupported source IDs
              are rejected and important outputs remain Draft.
            </p>
          </Card>
        </aside>
        <section className="chat">
          <div className="chat-thread">
            {!messages.length && !loading && (
              <div className="empty-chat">
                <Sparkles />
                <h3>What would you like to investigate?</h3>
                <p>
                  Ask about the portfolio, a forecast movement, risks,
                  contracts, meeting decisions, or lessons learned.
                </p>
              </div>
            )}
            {messages.map((m, i) => (
              <div className="exchange" key={i}>
                <div className="user-message">
                  <span>MR</span>
                  <p>{m.q}</p>
                </div>
                <div className="ai-message">
                  <div className="ai-symbol">
                    <Sparkles />
                  </div>
                  <div>
                    <div className="answer-meta">
                      <Badge tone="bronze">{m.type}</Badge>
                      <span>
                        Verified data · {Math.round(m.confidence * 100)}%
                        confidence
                      </span>
                    </div>
                    <h4>Answer</h4>
                    <p>{m.a}</p>
                    <div className="fact-row">
                      <span>CONTROL</span>
                      <p>
                        Values and retrieved clauses come from the database.
                        Gemini explains only the supplied evidence.
                      </p>
                    </div>
                    {m.sources.length > 0 && (
                      <div className="sources">
                        <b>Sources used</b>
                        {m.sources.map((s, j) => (
                          <button key={s} onClick={() => setSource(s)}>
                            {j === 0 ? (
                              <Database />
                            ) : j === 1 ? (
                              <FileText />
                            ) : (
                              <BookOpen />
                            )}
                            <span>
                              {s}
                              <small>Traceable evidence</small>
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                    <div className="feedback">
                      <span>Was this answer useful?</span>
                      <button onClick={async () => { if (m.runId) await api.feedback(m.runId, true); setNotice("Feedback recorded as helpful"); }}>
                        <ThumbsUp />
                      </button>
                      <button onClick={async () => { if (m.runId) await api.feedback(m.runId, false); setNotice("Feedback recorded for review"); }}>
                        <ThumbsDown />
                      </button>
                      <small>AI output · Draft</small>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="ai-loading">
                <LoaderCircle />
                <span>Routing question and verifying sources…</span>
              </div>
            )}
          </div>
          <div className="composer">
            <textarea
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  ask();
                }
              }}
              placeholder="Ask about projects, financials, forecasts, risks, contracts, or lessons learned…"
            />
            <button onClick={() => ask()} disabled={loading}>
              <Send />
            </button>
            <div>
              <span>
                <Sparkles /> Intelligent routing active
              </span>
              <small>Review important AI outputs.</small>
            </div>
          </div>
        </section>
      </div>
      {source && <Modal title="Traceable source" onClose={() => setSource(null)}><p>{source}</p><p>This source identifier was validated against retrieved database evidence before the answer was returned.</p></Modal>}
    </>
  );
}
