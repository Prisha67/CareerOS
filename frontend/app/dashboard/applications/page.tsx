"use client";
import { useEffect, useState } from "react";
import { addApp, listApps, setStatus } from "@/lib/api";
import { AppRec } from "@/types";

const STAGES = ["saved", "analysed", "ready", "applied", "assessment", "interview", "offer", "rejected", "withdrawn"];

export default function Applications() {
  const [apps, setApps] = useState<AppRec[]>([]);
  const [company, setCompany] = useState(""); const [role, setRole] = useState(""); const [link, setLink] = useState(true); const [error, setError] = useState("");
  useEffect(() => { listApps().then(setApps).catch(() => {}); }, []);
  const guard = async (f: () => Promise<void>) => { setError(""); try { await f(); } catch (e) { setError((e as Error).message); } };
  const field = { padding: 10, border: "1px solid var(--line)", borderRadius: 6, font: "inherit", background: "var(--panel)", color: "var(--ink)" } as const;

  return (
    <div className="stack">
      <div><h1>Applications</h1><p className="lead">Track every opportunity in one place. You submit applications yourself. CareerOS only records where each one stands.</p></div>
      <div className="row">
        <input aria-label="Company" style={field} placeholder="Company" value={company} onChange={e => setCompany(e.target.value)} />
        <input aria-label="Role" style={field} placeholder="Role" value={role} onChange={e => setRole(e.target.value)} />
        <label className="row"><input type="checkbox" checked={link} onChange={e => setLink(e.target.checked)} /> Link latest analysis</label>
        <button className="btn" onClick={() => guard(async () => { const a = await addApp(company, role, link ? localStorage.getItem("careeros:lastAnalysis") ?? "" : ""); setApps(x => [a, ...x]); setCompany(""); setRole(""); })}>Add</button>
      </div>
      {error && <p className="err" role="alert">{error}</p>}
      <table className="gaps"><thead><tr><th>Company</th><th>Role</th><th>Match</th><th>Status</th></tr></thead>
        <tbody>{apps.map(a => (
          <tr key={a.id}><td>{a.company}</td><td>{a.role}</td><td>{a.match ?? "–"}</td>
            <td><select aria-label={`Status for ${a.company}`} value={a.status} style={field} onChange={e => guard(async () => { const u = await setStatus(a.id, e.target.value); setApps(x => x.map(y => y.id === u.id ? { ...y, status: u.status } : y)); })}>
              {STAGES.map(s => <option key={s}>{s}</option>)}</select></td></tr>))}
          {apps.length === 0 && <tr><td colSpan={4} className="muted">No applications yet.</td></tr>}</tbody></table>
    </div>
  );
}
