import { Analysis } from "@/types";

export default function MatchResult({ a }: { a: Analysis }) {
  const m = a.match;
  return (
    <div className="stack">
      <section className="panel">
        <h2>{a.job_requirements.job_title || "Job"}</h2>
        <div className="score" style={{ margin: "12px 0" }}><b>{m.total}</b><span>out of 100 compatibility</span></div>
        {Object.entries(m.dimensions).map(([k, v]) => (
          <div className="dim" key={k}>
            <span style={{ textTransform: "capitalize" }}>{k}</span>
            <div className="bar"><i style={{ width: `${v}%` }} /></div>
            <em>{v}</em>
          </div>
        ))}
        <p className="muted" style={{ marginTop: 12 }}>{m.disclaimer}</p>
      </section>
      <section>
        <h2>Skill gap report</h2>
        <p className="muted">Each requirement and the evidence found for it.</p>
        <table className="gaps">
          <thead><tr><th>Skill</th><th>Type</th><th>Status</th><th>Evidence</th></tr></thead>
          <tbody>{m.gap_report.map(g => (
            <tr key={g.skill}><td>{g.skill}</td><td>{g.kind}</td>
              <td><span className={`chip${g.status === "matched" ? "" : " gap"}`}>{g.status}</span></td><td className="muted">{g.evidence}</td></tr>
          ))}</tbody>
        </table>
      </section>
      <section>
        <h2>Skills</h2>
        <div style={{ marginTop: 12 }}>
          {m.matched.map(s => <span className="chip" key={s}>{s}</span>)}
          {m.missing_required.map(s => <span className="chip gap" key={s}>{s}<small>required, missing</small></span>)}
          {m.missing_preferred.map(s => <span className="chip gap" key={s}>{s}<small>preferred, missing</small></span>)}
        </div>
      </section>
      {m.semantic_hints?.length > 0 && <section><h2>Possible evidence for gaps</h2><p className="muted">Found by meaning, not exact words. Not counted in the score.</p>
        <ul>{m.semantic_hints.map(h => <li key={h.skill}><b>{h.skill}</b>: “{h.evidence}”</li>)}</ul></section>}
      <section>
        <h2>What to do next</h2>
        <ul>{a.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
      </section>
    </div>
  );
}
