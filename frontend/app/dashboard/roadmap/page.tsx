"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { genRoadmap, getRoadmap, rescore, setMilestone } from "@/lib/api";
import { Roadmap } from "@/types";

export default function RoadmapPage() {
  const [aid, setAid] = useState<string | null>(null);
  const [rm, setRm] = useState<Roadmap | null>(null);
  const [score, setScore] = useState<{ before: number; after: number } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = localStorage.getItem("careeros:lastAnalysis");
    setAid(id);
    if (id) getRoadmap(id).then(setRm).catch(() => {});
  }, []);

  const guard = async (f: () => Promise<void>) => { setError(""); try { await f(); } catch (e) { setError((e as Error).message); } };
  if (!aid) return <div className="stack"><h1>Learning roadmap</h1><p className="lead">Analyse a job first. <Link href="/dashboard/job-analysis">Go to job analysis</Link></p></div>;
  const done = rm?.milestones.filter(m => m.done).length ?? 0;

  return (
    <div className="stack">
      <div><h1>Learning roadmap</h1><p className="lead">Ordered by what the job needs most. Ticking a milestone adds the skill to your profile as “roadmap”. Add real project evidence on the Resume page too.</p></div>
      {!rm && <div><button className="btn" onClick={() => guard(async () => setRm(await genRoadmap(aid)))}>Generate roadmap</button></div>}
      {rm && rm.milestones.length === 0 && <p>No gaps found for this job.</p>}
      {rm && rm.milestones.length > 0 && (
        <>
          <p><b>{done}</b> of {rm.milestones.length} milestones complete</p>
          <div>{rm.milestones.map(m => (
            <label className="ms" key={m.id}>
              <input type="checkbox" checked={m.done} onChange={e => guard(async () => setRm(await setMilestone(rm.id, m.id, e.target.checked)))} />
              <div><b>{m.priority}. {m.objective}</b> <span className="chip gap">{m.kind}</span>
                <p>Exercise: {m.exercise}</p><p>Project: {m.project}</p>
                <p className="muted">{[...m.prerequisites, ...m.resources].join(" · ")}</p></div>
            </label>
          ))}</div>
          <div className="row">
            <button className="btn" onClick={() => guard(async () => setScore(await rescore(aid)))}>Re-score this job</button>
            {score && <span role="status">Match: {score.before} → <b>{score.after}</b></span>}
          </div>
        </>
      )}
      {error && <p className="err" role="alert">{error}</p>}
    </div>
  );
}
