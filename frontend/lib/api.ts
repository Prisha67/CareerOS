import { Analysis, Analytics, AppRec, Doc, Evaluation, Profile, Roadmap } from "@/types";
import { getToken } from "@/lib/firebase";

async function authFetch(url: string, init: RequestInit = {}) {
  const t = await getToken();
  return globalThis.fetch(url, { ...init, headers: { ...(init.headers as object), ...(t ? { Authorization: `Bearer ${t}` } : {}) } });
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const USER = "demo"; // replaced by Firebase uid once auth is added

async function parse<T>(r: Response): Promise<T> {
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${r.status})`);
  }
  return r.json();
}

export const uploadResume = (file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return authFetch(`${BASE}/resume/upload?user_id=${USER}`, { method: "POST", body: fd }).then(r => parse<Profile>(r));
};
export const getProfile = () => authFetch(`${BASE}/profile/me?user_id=${USER}`).then(r => parse<Profile>(r));
export const analyzeJob = (job_description: string) =>
  authFetch(`${BASE}/applications/match`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: USER, job_description }),
  }).then(r => parse<Analysis>(r));
export const getAnalysis = (id: string) => authFetch(`${BASE}/analysis/${id}`).then(r => parse<Analysis>(r));
export const saveProfile = (p: Profile) =>
  authFetch(`${BASE}/profile/me?user_id=${USER}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...p, skills: p.skills.map(s => s.name), projects: p.projects.map(x => x.text) }),
  }).then(r => parse<Profile>(r));

const post = <T,>(path: string, body: object) =>
  authFetch(`${BASE}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: USER, ...body }) }).then(r => parse<T>(r));
const patch = <T,>(path: string, body: object) =>
  authFetch(`${BASE}${path}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(r => parse<T>(r));

export const makeDoc = (kind: "resume/tailor" | "documents/cover-letter" | "documents/answer", analysis_id: string, question = "") =>
  post<Doc>(`/${kind}`, { analysis_id, question });
export const updateDoc = (id: string, b: { text?: string; approved?: boolean }) => patch<Doc>(`/documents/${id}`, b);
export const listDocs = (analysis_id: string) => authFetch(`${BASE}/documents?analysis_id=${analysis_id}`).then(r => parse<Doc[]>(r));
export const genRoadmap = (analysis_id: string) => post<Roadmap>("/roadmap/generate", { analysis_id });
export const getRoadmap = (analysis_id: string) => authFetch(`${BASE}/roadmap?analysis_id=${analysis_id}`).then(r => parse<Roadmap | null>(r));
export const setMilestone = (rid: string, mid: string, done: boolean) => patch<Roadmap>(`/roadmap/${rid}/milestones/${mid}`, { done, user_id: USER });
export const rescore = (aid: string) => authFetch(`${BASE}/analysis/${aid}/rescore?user_id=${USER}`, { method: "POST" }).then(r => parse<{ before: number; after: number }>(r));

export const startInterview = (analysis_id: string) => post<{ id: string; questions: { id: string; category: string; text: string }[] }>("/interviews/start", { analysis_id });
export const answerQ = (interview_id: string, question_id: string, answer: string) =>
  post<{ evaluation: Evaluation; complete: boolean; average: number }>("/interviews/answer", { interview_id, question_id, answer });
export const listApps = () => authFetch(`${BASE}/applications?user_id=${USER}`).then(r => parse<AppRec[]>(r));
export const addApp = (company: string, role: string, analysis_id = "") => post<AppRec>("/applications", { company, role, analysis_id });
export const setStatus = (id: string, status: string) => patch<AppRec>(`/applications/${id}`, { status, user_id: USER });
export const getAnalytics = () => authFetch(`${BASE}/analytics?user_id=${USER}`).then(r => parse<Analytics>(r));
export const deleteMyData = () => authFetch(`${BASE}/profile/me?user_id=${USER}`, { method: "DELETE" }).then(r => parse<{ deleted: boolean }>(r));
