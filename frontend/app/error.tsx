"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return <div className="page-heading"><div className="eyebrow">DOCUMENTATION</div><h1>This page is unavailable</h1><p>The source document could not be loaded. Please retry or ask the maintainer to check the documentation files.</p><button className="retry-button" onClick={reset}>Try again</button></div>;
}
