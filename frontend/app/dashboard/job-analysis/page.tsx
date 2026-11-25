"use client";
import { useState } from "react";
import Link from "next/link";
import { analyzeJob } from "@/lib/api";
import MatchResult from "@/components/MatchResult";
import { Analysis } from "@/types";

export default function JobAnalysisPage() {
  const [jd, setJd] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);

  async function run() {
    setError(""); setBusy(true);
    try {
      const a = await analyzeJob(jd);
      setResult(a);
      if (a.id) localStorage.setItem("careeros:lastAnalysis", a.id);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="stack">
      <div><h1>Job analysis</h1>
        <p className="lead">Paste a job description. Put “Preferred” or “Nice to have” before optional skills so they are scored separately.</p></div>
      <textarea aria-label="Job description" value={jd} onChange={e => setJd(e.target.value)} placeholder="Machine Learning Intern&#10;Requirements: Python, SQL…&#10;Preferred: PyTorch, NLP" />
      <div className="row">
        <button className="btn" disabled={busy || jd.trim().length < 20} onClick={run}>{busy ? "Analysing…" : "Analyse match"}</button>
        {error && <span className="err" role="alert">{error}{error.includes("resume") && <> <Link href="/dashboard/resume">Add your resume</Link></>}</span>}
      </div>
      {result && <MatchResult a={result} />}
    </div>
  );
}
