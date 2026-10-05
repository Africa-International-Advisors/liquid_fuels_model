import { isDocumentKey, readDocument } from "@/lib/documents";
export const dynamic = "force-dynamic";
export async function GET(_request: Request, { params }: { params: Promise<{ document: string }> }) {
  const { document } = await params;
  if (!isDocumentKey(document)) return new Response("Document not found", { status: 404 });
  try {
    const source = await readDocument(document);
    return new Response(source.markdown, { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
  } catch { return new Response("Document unavailable", { status: 503 }); }
}
