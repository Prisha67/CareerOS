"use client";
import { useState } from "react";
import { saveProfile } from "@/lib/api";
import { Profile } from "@/types";

export default function ProfileEditor({ profile, onSaved }: { profile: Profile; onSaved: (p: Profile) => void }) {
  const [p, setP] = useState(profile);
  const [skill, setSkill] = useState("");
  const [msg, setMsg] = useState("");
  const lines = (v: string) => v.split("\n");

  function addSkill() {
    const n = skill.trim();
    if (n && !p.skills.some(s => s.name.toLowerCase() === n.toLowerCase())) setP({ ...p, skills: [...p.skills, { name: n, sources: ["manual"] }] });
    setSkill("");
  }
  async function save() {
    setMsg("");
    try { const s = await saveProfile(p); setP(s); onSaved(s); setMsg("Saved"); }
    catch (e) { setMsg((e as Error).message); }
  }

  return (
    <div className="stack">
      {p.warnings.length > 0 && <div className="warn" role="status"><b>Check your profile</b><ul>{p.warnings.map(w => <li key={w}>{w}</li>)}</ul></div>}
      <div className="row">
        <label className="field">Name<input value={p.name} onChange={e => setP({ ...p, name: e.target.value })} /></label>
        <label className="field">Email<input value={p.email} onChange={e => setP({ ...p, email: e.target.value })} /></label>
        <label className="field">Degree<input value={p.degree} onChange={e => setP({ ...p, degree: e.target.value })} /></label>
        <label className="field">Branch<input value={p.branch} onChange={e => setP({ ...p, branch: e.target.value })} /></label>
      </div>
      <div>
        <h2>Skills</h2>
        <div style={{ margin: "10px 0" }}>{p.skills.map(s => (
          <span className="chip" key={s.name}>{s.name}<small>{s.sources.join(", ")}</small>
            <button aria-label={`Remove ${s.name}`} onClick={() => setP({ ...p, skills: p.skills.filter(x => x.name !== s.name) })}>×</button></span>
        ))}</div>
        <div className="row">
          <input aria-label="Add a skill" value={skill} placeholder="Add a skill" onChange={e => setSkill(e.target.value)} onKeyDown={e => e.key === "Enter" && addSkill()}
            style={{ padding: 10, border: "1px solid var(--line)", borderRadius: 6, font: "inherit", background: "var(--panel)", color: "var(--ink)" }} />
          <button className="btn ghost" onClick={addSkill}>Add skill</button>
        </div>
      </div>
      <label className="field">Education<input value={p.education} onChange={e => setP({ ...p, education: e.target.value })} /></label>
      <label className="field">Projects (one per line)<textarea value={p.projects.map(x => x.text).join("\n")} onChange={e => setP({ ...p, projects: lines(e.target.value).map(t => ({ text: t, technologies: [] })) })} /></label>
      <label className="field">Experience (one per line)<textarea value={p.experience.join("\n")} onChange={e => setP({ ...p, experience: lines(e.target.value) })} /></label>
      <div className="row"><button className="btn" onClick={save}>Save changes</button><span role="status">{msg}</span></div>
    </div>
  );
}
