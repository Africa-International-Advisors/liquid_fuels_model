import Link from "next/link";
import { ArrowUpRight, GitBranch, Layers3 } from "lucide-react";
import { readDocument, sectionBody } from "@/lib/documents";
import { Markdown } from "@/components/markdown";
import { PageHeading } from "@/components/page-heading";
export default async function Home() {
  const [overview, hypothesis] = await Promise.all([readDocument("overview"), readDocument("hypothesis")]);
  const why = sectionBody(overview.sections, "Why this exists");
  const status = sectionBody(hypothesis.sections, "At-a-glance summary");
  const implementation = sectionBody(overview.sections, "Current implementation");
  return <><PageHeading number="01" title="Model overview" description="Understand what the model answers, how demand is built up, and where the work stands." source={overview.source} document="overview"/>
    <div className="reader-layout"><div className="reader-main">
      <section className="document-section" id="purpose"><h2>The question behind the model</h2><Markdown>{why ?? overview.preamble}</Markdown></section>
      <div className="reading-paths"><Link href="/hypothesis-tree" prefetch={false}><GitBranch size={22}/><div><h3>Explore the demand drivers</h3><p>Follow each sector from assumptions to fuel demand.</p></div><ArrowUpRight size={19}/></Link><Link href="/architecture" prefetch={false}><Layers3 size={22}/><div><h3>Understand the architecture</h3><p>See the design decisions and the model workflow.</p></div><ArrowUpRight size={19}/></Link></div>
      {status && <section className="document-section" id="segments"><div className="section-kicker">MODEL COVERAGE</div><h2>Segments at a glance</h2><Markdown>{status}</Markdown><p className="small-note">MODELLED describes the calculation approach, not validation status. HELD means a base volume scaled by a driver.</p></section>}
      {implementation && <section className="document-section" id="current"><h2>Current implementation</h2><Markdown>{implementation}</Markdown></section>}
    </div><aside className="page-index" aria-label="On this page"><div className="eyebrow">ON THIS PAGE</div><a href="#purpose">Purpose</a><a href="#segments">Segment coverage</a><a href="#current">Current implementation</a><div className="index-note"><span className="status-dot"/><p>Working model<br/><strong>Outputs remain provisional.</strong></p></div></aside></div></>;
}
