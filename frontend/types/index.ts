export type Profile = {
  name: string; email: string; degree: string; branch: string; warnings: string[];
  skills: { name: string; sources: string[] }[];
  projects: { text: string; technologies: string[] }[];
  experience: string[];
  education: string;
  certifications: string[];
};
export type Match = {
  total: number;
  dimensions: Record<string, number>;
  weights: Record<string, number>;
  matched: string[];
  missing_required: string[];
  missing_preferred: string[];
  not_evidenced_in_projects: string[];
  semantic_hints: { skill: string; evidence: string; similarity: number }[];
  partial: { skill: string; via: string }[];
  gap_report: { skill: string; kind: string; status: "matched" | "related" | "missing"; evidence: string }[];
  disclaimer: string;
};
export type Analysis = {
  id?: string;
  job_requirements: { job_title: string; required_skills: string[]; preferred_skills: string[] };
  match: Match;
  recommendations: string[];
};
export type Doc = { id: string; type: string; title: string; text: string; used_llm: boolean; notes: string[]; status: "pending_approval" | "approved" };
export type Milestone = { id: string; priority: number; skill: string; kind: string; objective: string; exercise: string; project: string; prerequisites: string[]; resources: string[]; done: boolean };
export type Roadmap = { id: string; analysis_id: string; milestones: Milestone[] };
export type Evaluation = { score: number; strengths: string[]; improve: string[]; coach_note: string | null; dimensions: Record<string, number> };
export type AppRec = { id: string; company: string; role: string; status: string; match: number | null };
export type Analytics = { jobs_analysed: number; applications: number; applied: number; by_stage: Record<string, number>; interview_rate: number | null; offer_rate: number | null;
  top_missing_skills: [string, number][]; match_trend: number[]; interview_avg: number | null; roadmap_progress: { done: number; total: number } };
