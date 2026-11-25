import { Profile } from "@/types";

export default function ProfileView({ profile }: { profile: Profile }) {
  return (
    <div className="stack">
      <section>
        <h2>Skills found ({profile.skills.length})</h2>
        <p className="muted">The section of your resume each skill came from is shown beside it.</p>
        <div style={{ marginTop: 12 }}>
          {profile.skills.length === 0 && <p>No known skills detected. Add a “Skills” section to your resume.</p>}
          {profile.skills.map(s => (
            <span className="chip" key={s.name}>{s.name}<small>{s.sources.join(", ")}</small></span>
          ))}
        </div>
      </section>
      <section>
        <h2>Projects ({profile.projects.length})</h2>
        {profile.projects.length === 0 && <p className="muted">No “Projects” section found.</p>}
        <ul>{profile.projects.map((p, i) => (
          <li key={i}>{p.text}{p.technologies.length > 0 && <span className="muted"> — {p.technologies.join(", ")}</span>}</li>
        ))}</ul>
      </section>
      <section>
        <h2>Education</h2>
        <p>{profile.education || <span className="muted">No “Education” section found.</span>}</p>
      </section>
    </div>
  );
}
