"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getAnalysis, getProfile } from "@/lib/api";
import AnalyticsPanel from "@/components/AnalyticsPanel";
import { Analysis, Profile } from "@/types";

export default function Overview() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [last, setLast] = useState<Analysis | null>(null);

  useEffect(() => {
    getProfile().then(setProfile).catch(() => {});
    const id = localStorage.getItem("careeros:lastAnalysis");
    if (id) getAnalysis(id).then(setLast).catch(() => {});
  }, []);

  const parts = profile ? [profile.skills.length > 0, profile.projects.length > 0, !!profile.education, profile.experience.length > 0] : [];
  const complete = profile ? Math.round((parts.filter(Boolean).length / 4) * 100) : 0;

  return (
    <div className="stack">
      <div><h1>Overview</h1><p className="lead">Where your profile stands and what to do next.</p></div>
      <ul className="checklist panel">
        <li><span>Resume uploaded</span>{profile ? <span className="done">Done — profile {complete}% complete</span> : <Link href="/dashboard/resume">Add resume</Link>}</li>
        <li><span>Profile sections</span><span className="muted">{profile ? `${profile.skills.length} skills · ${profile.projects.length} projects` : "Waiting for resume"}</span></li>
        <li><span>First job analysed</span>{last ? <span className="done">Done — {last.match.total}/100 for {last.job_requirements.job_title}</span> : profile ? <Link href="/dashboard/job-analysis">Analyse a job</Link> : <span className="muted">Needs resume first</span>}</li>
      </ul>
      {last && (
        <section>
          <h2>Biggest gaps in your last analysis</h2>
          <div style={{ marginTop: 12 }}>
            {[...last.match.missing_required, ...last.match.missing_preferred].slice(0, 8).map(s => <span className="chip gap" key={s}>{s}</span>)}
            {last.match.missing_required.length + last.match.missing_preferred.length === 0 && <p>No missing skills. Check the next steps on the job analysis page.</p>}
          </div>
        </section>
      )}
      <AnalyticsPanel />
    </div>
  );
}
