import type { Metadata } from "next";
import { readDocument } from "@/lib/documents";
import { Markdown } from "@/components/markdown";
import { PageHeading } from "@/components/page-heading";
export const metadata: Metadata = { title: "Architecture" };
export default async function ArchitecturePage() {
  const doc = await readDocument("architecture");
  return <><PageHeading number="03" title="Model architecture" description="The structure, modelling commitments and working conventions behind the Python rebuild." source={doc.source} document="architecture"/>
    <div className="reader-layout"><div className="reader-main">{doc.sections.map((section) => <section className="document-section" key={section.id} id={section.id}><h2>{section.title}</h2><Markdown>{section.body}</Markdown></section>)}</div><aside className="page-index" aria-label="On this page"><div className="eyebrow">ON THIS PAGE</div>{doc.sections.map((section) => <a key={section.id} href={`#${section.id}`}>{section.title}</a>)}</aside></div></>;
}
