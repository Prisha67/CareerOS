"use client";
import { useRef, useState } from "react";
import { uploadResume } from "@/lib/api";
import { Profile } from "@/types";

const OK = [".pdf", ".docx", ".txt"];

export default function ResumeUpload({ onDone }: { onDone: (p: Profile) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handle(file?: File) {
    if (!file) return;
    if (!OK.some(e => file.name.toLowerCase().endsWith(e))) { setError("Use a PDF, DOCX or TXT file."); return; }
    setError(""); setBusy(true);
    try { onDone(await uploadResume(file)); }
    catch (e) { setError((e as Error).message + " — is the backend running on port 8000?"); }
    finally { setBusy(false); }
  }

  return (
    <div>
      <div
        className={`drop${over ? " over" : ""}`} role="button" tabIndex={0}
        onClick={() => input.current?.click()}
        onKeyDown={e => (e.key === "Enter" || e.key === " ") && input.current?.click()}
        onDragOver={e => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={e => { e.preventDefault(); setOver(false); handle(e.dataTransfer.files[0]); }}
      >
        <h3>{busy ? "Reading your resume…" : "Drop your resume here"}</h3>
        <p className="muted">or click to choose a PDF, DOCX or TXT file</p>
        <input ref={input} type="file" hidden accept=".pdf,.docx,.txt" onChange={e => handle(e.target.files?.[0])} />
      </div>
      {error && <p className="err" role="alert" style={{ marginTop: 12 }}>{error}</p>}
    </div>
  );
}
