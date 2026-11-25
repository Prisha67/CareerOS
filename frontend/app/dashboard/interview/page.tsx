"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { answerQ, startInterview } from "@/lib/api";
import { Evaluation } from "@/types";

type Q = { id: string; category: string; text: string };

export default function InterviewPage() {
  const [aid, setAid] = useState<string | null>(null);
  const [iv, setIv] = useState<{ id: string; questions: Q[] } | null>(null);
  const [i, setI] = useState(0); const [ans, setAns] = useState(""); const [ev, setEv] = useState<Evaluation | null>(null);
  const [avg, setAvg] = useState<number | null>(null); const [done, setDone] = useState(false); const [error, setError] = useState("");
  useEffect(() => setAid(localStorage.getItem("careeros:lastAnalysis")), []);

  const guard = async (f: () => Promise<void>) => { setError(""); try { await f(); } catch (e) { setError((e as Error).message); } };
  if (!aid) return <div className="stack"><h1>Mock interview</h1><p className="lead">Analyse a job first. <Link href="/dashboard/job-analysis">Go to job analysis</Link></p></div>;
  const q = iv?.questions[i];
  return (
    <div className="stack">
      <div><h1>Mock interview</h1><p className="lead">Questions come from the job and your projects. Scores use a transparent rubric (coverage, depth, clarity, STAR structure), so treat them as practice feedback.</p></div>
      {!iv && <div><button className="btn" onClick={() => guard(async () => setIv(await startInterview(aid)))}>Start interview</button></div>}
      {iv && q && !done && (
        <section className="panel stack" style={{ gap: 14 }}>
          <p className="muted">Question {i + 1} of {iv.questions.length} · {q.category}</p>
          <h2>{q.text}</h2>
          <textarea aria-label="Your answer" value={ans} onChange={e => setAns(e.target.value)} disabled={!!ev} />
          {!ev ? <div><button className="btn" disabled={ans.trim().length < 5} onClick={() => guard(async () => { const r = await answerQ(iv.id, q.id, ans); setEv(r.evaluation); setAvg(r.average); })}>Submit answer</button></div> : (
            <div className="stack" style={{ gap: 10 }}>
              <div className="score"><b>{ev.score}</b><span>out of 10</span></div>
              {ev.strengths.length > 0 && <div><h3>Strengths</h3><ul>{ev.strengths.map(s => <li key={s}>{s}</li>)}</ul></div>}
              {ev.improve.length > 0 && <div><h3>To improve</h3><ul>{ev.improve.map(s => <li key={s}>{s}</li>)}</ul></div>}
              {ev.coach_note && <p className="muted">{ev.coach_note}</p>}
              <div><button className="btn" onClick={() => { if (i + 1 < iv.questions.length) { setI(i + 1); setAns(""); setEv(null); } else setDone(true); }}>{i + 1 < iv.questions.length ? "Next question" : "Finish"}</button></div>
            </div>)}
        </section>)}
      {done && <section className="panel"><h2>Interview complete</h2><p className="lead">Average score: <b>{avg}</b> / 10. Your trend appears on the Overview page.</p></section>}
      {error && <p className="err" role="alert">{error}</p>}
    </div>
  );
}
