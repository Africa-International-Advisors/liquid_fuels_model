import { documents, readDocument, type DocumentKey } from "@/lib/documents";
export const dynamic = "force-dynamic";
export async function GET() {
  try {
    await Promise.all((Object.keys(documents) as DocumentKey[]).map((key) => readDocument(key)));
    return Response.json({ status: "ok" });
  } catch { return Response.json({ status: "documents-unavailable" }, { status: 503 }); }
}
