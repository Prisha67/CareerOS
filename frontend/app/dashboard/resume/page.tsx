"use client";
import { useEffect, useState } from "react";
import ResumeUpload from "@/components/ResumeUpload";
import ProfileEditor from "@/components/ProfileEditor";
import { getProfile } from "@/lib/api";
import { Profile } from "@/types";

export default function ResumePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  useEffect(() => { getProfile().then(setProfile).catch(() => {}); }, []);
  return (
    <div className="stack">
      <div><h1>Your resume</h1><p className="lead">Upload it once. CareerOS reads out your skills, projects and education so it can compare them with jobs.</p></div>
      <ResumeUpload onDone={setProfile} />
      {profile && <div className="panel"><ProfileEditor key={JSON.stringify(profile)} profile={profile} onSaved={setProfile} /></div>}
    </div>
  );
}
