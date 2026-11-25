"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import DocCard from "@/components/DocCard";
import { listDocs, makeDoc } from "@/lib/api";
import { Doc } from "@/types";

export default function Assistant() {
  const [aid, setAid] = useState<string | null>(null);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const id = localStorage.getItem("careeros:lastAnalysis");
    setAid(id);
    if (id) listDocs(id).then(setDocs).catch(() => {});
  }, []);

  async function run(kind: Parameters<typeof makeDoc>[0]) {
    if (!aid) return;
    setError(""); setBusy(kind);
    try { const d = await makeDoc(kind, aid, q); setDocs(x => [d, ...x]); }
    catch (e) { setError((e as Error).message); } finally { setBusy(""); }
  }
  const replace = (d: Doc) => setDocs(x => x.map(y => (y.id === d.id ? d : y)));

  if (!aid) return <div className="stack"><h1>Application drafts</h1><p className="lead">Analyse a job first. <Link href="/dashboard/job-analysis">Go to job analysis</Link></p></div>;
  return (
    <div className="stack">
      <div><h1>Application drafts</h1><p className="lead">Drafts for your latest analysed job. Nothing is final until you approve it, and drafts that add claims not in your profile are replaced by a safe template.</p></div>
      <div className="row">
        <button className="btn" disabled={!!busy} onClick={() => run("resume/tailor")}>{busy === "resume/tailor" ? "Working…" : "Tailor resume"}</button>
        <button className="btn" disabled={!!busy} onClick={() => run("documents/cover-letter")}>{busy === "documents/cover-letter" ? "Working…" : "Write cover letter"}</button>
      </div>
      <div className="row">
        <input aria-label="Application question" value={q} onChange={e => setQ(e.target.value)} placeholder="Paste an application question, e.g. Why do you want this role?"
          style={{ flex: 1, minWidth: 240, padding: 10, border: "1px solid var(--line)", borderRadius: 6, font: "inherit", background: "var(--panel)", color: "var(--ink)" }} />
        <button className="btn ghost" disabled={!!busy || !q.trim()} onClick={() => run("documents/answer")}>Draft answer</button>
      </div>
      {error && <p className="err" role="alert">{error}</p>}
      {docs.map(d => <DocCard key={d.id} doc={d} onChange={replace} />)}
    </div>
  );
}
