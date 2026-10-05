import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function Markdown({ children }: { children: string }) {
  return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml
    components={{ table: ({ children }) => <div className="table-scroll" tabIndex={0} role="region" aria-label="Scrollable documentation table"><table>{children}</table></div> }}
  >{children}</ReactMarkdown></div>;
}
