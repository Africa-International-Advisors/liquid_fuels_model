import { FileText } from "lucide-react";
import type { DocumentKey } from "@/lib/documents";
export function PageHeading({ number, title, description, source, document }: {number: string; title: string; description: string; source: string; document: DocumentKey}) {
  return <header className="page-heading"><div className="eyebrow">HANDBOOK / {number}</div><h1>{title}</h1><p>{description}</p><a className="source-link" href={`/source/${document}`}><FileText size={14}/><span>{source}</span></a></header>;
}
