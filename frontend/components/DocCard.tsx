"use client";
import { useState } from "react";
import { updateDoc } from "@/lib/api";
import { Doc } from "@/types";

export default function DocCard({ doc, onChange }: { doc: Doc; onChange: (d: Doc) => void }) {
  const [text, setText] = useState(doc.text);
  const approved = doc.status === "approved";
  const dirty = text !== doc.text;
  return (
    <section className="panel doc stack" style={{ gap: 14 }}>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h2>{doc.title}</h2>
        <span className={`badge${approved ? " ok" : ""}`}>{approved ? "Approved" : "Needs your approval"}</span>
      </div>
      <p className="muted">{doc.used_llm ? "Drafted with Mistral and checked against your profile." : "Template draft (no AI model used)."}</p>
      {doc.notes.map(n => <p className="warn" key={n} role="status">{n}</p>)}
      <textarea aria-label={doc.title} value={text} onChange={e => setText(e.target.value)} />
      <div className="row">
        <button className="btn ghost" disabled={!dirty} onClick={async () => onChange(await updateDoc(doc.id, { text }))}>Save edits</button>
        <button className="btn" disabled={dirty || approved} onClick={async () => onChange(await updateDoc(doc.id, { approved: true }))}>Approve</button>
        <button className="btn ghost" onClick={() => navigator.clipboard.writeText(text)}>Copy</button>
      </div>
      <p className="muted">Review every line. Only approve what is true about you.</p>
    </section>
  );
}
