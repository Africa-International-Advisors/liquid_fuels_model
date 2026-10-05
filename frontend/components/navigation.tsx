"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, GitBranch, Layers3, ArrowUpRight } from "lucide-react";
const links = [
  { href: "/", label: "Overview", icon: BookOpen, number: "01" },
  { href: "/hypothesis-tree", label: "Hypothesis tree", icon: GitBranch, number: "02" },
  { href: "/architecture", label: "Architecture", icon: Layers3, number: "03" },
];
export function Navigation() {
  const pathname = usePathname();
  return <aside className="sidebar">
    <Link href="/" className="brand" aria-label="Liquid fuels handbook home"><span className="brand-mark">LF</span><span>Liquid fuels<span className="brand-sub">MODEL HANDBOOK</span></span></Link>
    <div className="nav-label">DOCUMENTATION</div>
    <nav aria-label="Main navigation">{links.map(({ href, label, icon: Icon, number }) => <Link key={href} href={href} prefetch={false} aria-current={pathname === href ? "page" : undefined} className={`nav-link ${pathname === href ? "active" : ""}`}><Icon size={18}/><span>{label}</span><span className="nav-number">{number}</span></Link>)}</nav>
    <div className="sidebar-note"><span className="eyebrow">A WORKING REFERENCE</span><p>The assumptions, drivers and design behind the forecast.</p><a href="/source/overview" className="source-nav">Read the source <ArrowUpRight size={14}/></a></div>
    <div className="sidebar-footer"><span className="status-dot"/> Internal ? Read only</div>
  </aside>;
}
