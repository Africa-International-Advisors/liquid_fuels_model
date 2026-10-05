import { readFile, stat } from "node:fs/promises";
import path from "node:path";

export const documents = {
  overview: { path: "README.md", title: "Model overview" },
  hypothesis: { path: "docs/methodology/demand_hypothesis_tree.md", title: "Demand hypothesis tree" },
  architecture: { path: "CLAUDE.md", title: "Architecture" },
} as const;
export type DocumentKey = keyof typeof documents;
export type Section = { title: string; body: string; id: string };

export function isDocumentKey(value: string): value is DocumentKey {
  return Object.hasOwn(documents, value);
}

// Accept only the explicit document keys above. No user-supplied filesystem paths.
export async function readDocument(key: DocumentKey, root = process.env.LFM_DOCS_ROOT ?? path.resolve(/* turbopackIgnore: true */ process.cwd(), "..")) {
  if (!isDocumentKey(key)) throw new Error("Unknown document");
  const relativePath = documents[key].path;
  const filename = path.join(/* turbopackIgnore: true */ root, relativePath);
  const [markdown, info] = await Promise.all([readFile(/* turbopackIgnore: true */ filename, "utf8"), stat(/* turbopackIgnore: true */ filename)]);
  return { markdown, source: relativePath, modified: info.mtime.toISOString(), ...splitSections(markdown) };
}

export function splitSections(markdown: string) {
  const sections: Section[] = [];
  const preamble: string[] = [];
  let current: { title: string; lines: string[] } | undefined;
  let fence = "";
  const finish = () => {
    if (!current) return;
    const slug = current.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    sections.push({ title: current.title, body: current.lines.join("\n").trim(), id: `${slug || "section"}-${sections.length}` });
  };
  for (const line of markdown.replace(/\r\n/g, "\n").split("\n")) {
    const marker = /^\s{0,3}(`{3,}|~{3,})/.exec(line)?.[1];
    if (marker && (!fence || (marker[0] === fence[0] && marker.length >= fence.length))) {
      fence = fence ? "" : marker;
    }
    const heading = !fence && /^##\s+(.+?)(?:\s+#+)?$/.exec(line);
    if (heading) {
      finish(); current = { title: heading[1].trim(), lines: [] };
    } else if (current) current.lines.push(line);
    else preamble.push(line);
  }
  finish();
  return { preamble: preamble.join("\n").replace(/^# [^\n]*\n?/, "").trim(), sections };
}

export function sectionBody(sections: Section[], title: string) {
  return sections.find((section) => section.title.toLowerCase() === title.toLowerCase())?.body;
}
