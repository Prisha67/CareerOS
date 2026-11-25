"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { auth, authEnabled } from "@/lib/firebase";
import { deleteMyData } from "@/lib/api";

export default function Login() {
  const r = useRouter();
  const [email, setEmail] = useState(""); const [pw, setPw] = useState(""); const [msg, setMsg] = useState("");
  const go = async (f: typeof signInWithEmailAndPassword) => { try { await f(auth!, email, pw); r.push("/dashboard"); } catch (e) { setMsg((e as Error).message); } };
  return (
    <main className="main stack">
      <h1>Account</h1>
      {!authEnabled ? <p className="lead">Sign-in is not configured, so CareerOS runs in single-user demo mode. Set the NEXT_PUBLIC_FIREBASE_* variables to enable it.</p> : (
        <div className="panel stack" style={{ maxWidth: 380 }}>
          <label className="field">Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} /></label>
          <label className="field">Password<input type="password" value={pw} onChange={e => setPw(e.target.value)} /></label>
          <div className="row"><button className="btn" onClick={() => go(signInWithEmailAndPassword)}>Sign in</button>
            <button className="btn ghost" onClick={() => go(createUserWithEmailAndPassword)}>Create account</button>
            <button className="btn ghost" onClick={() => signOut(auth!)}>Sign out</button></div>
        </div>)}
      <div className="panel"><h2>Your data</h2><p className="muted">Delete your profile, analyses, drafts, interviews and applications.</p>
        <button className="btn ghost" style={{ marginTop: 10 }} onClick={async () => { if (confirm("Delete all your CareerOS data?")) { await deleteMyData(); setMsg("Your data was deleted."); } }}>Delete my data</button></div>
      {msg && <p role="status" className="err">{msg}</p>}
    </main>
  );
}
