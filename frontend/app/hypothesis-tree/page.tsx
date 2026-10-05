import type { Metadata } from "next";
import { readDocument, sectionBody } from "@/lib/documents";
import { Markdown } from "@/components/markdown";
import { PageHeading } from "@/components/page-heading";
import { SectionAccordion } from "@/components/section-accordion";
export const metadata: Metadata = { title: "Demand hypothesis tree" };
export default async function HypothesisPage() {
  const doc = await readDocument("hypothesis");
  const segments = doc.sections.filter((section) => /^\d+\./.test(section.title));
  const summary = sectionBody(doc.sections, "At-a-glance summary");
  const legend = sectionBody(doc.sections, "Status tags");
  const other = doc.sections.filter((section) => !/^\d+\./.test(section.title) && !["Status tags", "At-a-glance summary"].includes(section.title));
  return <><PageHeading number="02" title="Demand hypothesis tree" description="Trace the drivers behind each segment. Open a section to see what is quantified, provisional or not yet modelled." source={doc.source} document="hypothesis"/>
    <div className="reader-layout"><div className="reader-main"><Markdown>{doc.preamble}</Markdown>
      {legend && <section className="legend-box"><h2>Reading the tree</h2><Markdown>{legend}</Markdown></section>}
      {summary && <section className="document-section"><h2>At a glance</h2><Markdown>{summary}</Markdown></section>}
      <section className="document-section"><div className="section-kicker">DRIVER DECOMPOSITION</div><h2>Browse by segment</h2><SectionAccordion items={segments.map((section) => ({...section, content: <Markdown>{section.body}</Markdown>}))}/></section>
      {other.map((section) => <section className="document-section" key={section.id} id={section.id}><h2>{section.title}</h2><Markdown>{section.body}</Markdown></section>)}
    </div><aside className="page-index" aria-label="Tree legend"><div className="eyebrow">INPUT STATUS</div><p><span className="legend-tag">Q</span> Quantified</p><p><span className="legend-tag provisional">P</span> Provisional</p><p><span className="legend-tag muted">N</span> Not modelled</p><p className="small-note">A sourced value still needs review. These tags are not release approval.</p></aside></div></>;
}
