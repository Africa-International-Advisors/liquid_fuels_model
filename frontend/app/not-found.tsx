import Link from "next/link";
export default function NotFound() {
  return <div className="page-heading"><div className="eyebrow">404 / NOT FOUND</div><h1>Page not found</h1><p>Choose a section from the handbook navigation.</p><Link className="source-link" href="/">Return to the overview</Link></div>;
}
