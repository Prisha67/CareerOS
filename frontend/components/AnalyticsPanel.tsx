"use client";
import { useEffect, useState } from "react";
import { getAnalytics } from "@/lib/api";
import { Analytics } from "@/types";

export default function AnalyticsPanel() {
  const [a, setA] = useState<Analytics | null>(null);
  useEffect(() => { getAnalytics().then(setA).catch(() => {}); }, []);
  if (!a) return null;
  const pct = (v: number | null) => (v === null ? "–" : `${v}%`);
  return (
    <section className="stack" style={{ gap: 16 }}>
      <h2>Your progress</h2>
      <div className="row" style={{ gap: 28 }}>
        {[["Jobs analysed", a.jobs_analysed], ["Applied", a.applied], ["Interview rate", pct(a.interview_rate)], ["Offer rate", pct(a.offer_rate)],
          ["Mock interview avg", a.interview_avg ?? "–"], ["Roadmap", `${a.roadmap_progress.done}/${a.roadmap_progress.total}`]].map(([k, v]) => (
          <div key={String(k)}><div className="muted">{k}</div><b style={{ fontSize: "1.6rem" }}>{v}</b></div>))}
      </div>
      {a.match_trend.length > 0 && <div><div className="muted">Match score by analysis</div>
        {a.match_trend.map((v, i) => <div className="dim" key={i}><span>#{i + 1}</span><div className="bar"><i style={{ width: `${v}%` }} /></div><em>{v}</em></div>)}</div>}
      {a.top_missing_skills.length > 0 && <div><div className="muted">Most frequently missing skills</div>
        {a.top_missing_skills.map(([s, n]) => <span className="chip gap" key={s}>{s}<small>×{n}</small></span>)}</div>}
    </section>
  );
}
