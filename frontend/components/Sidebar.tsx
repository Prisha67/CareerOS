"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/resume", label: "Resume" },
  { href: "/dashboard/job-analysis", label: "Job analysis" },
  { href: "/dashboard/assistant", label: "Application drafts" },
  { href: "/dashboard/roadmap", label: "Learning roadmap" },
  { href: "/dashboard/interview", label: "Mock interview" },
  { href: "/dashboard/applications", label: "Applications" },
  { href: "/login", label: "Account" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="side">
      <div className="brand">CareerOS</div>
      <nav className="nav" aria-label="Main">
        {LINKS.map(l => (
          <Link key={l.href} href={l.href} aria-current={path === l.href ? "page" : undefined}>{l.label}</Link>
        ))}
      </nav>
    </aside>
  );
}
