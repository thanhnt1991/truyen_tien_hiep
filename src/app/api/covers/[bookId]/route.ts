import { NextResponse } from "next/server";
import { getNewBookPublicId, isNewBookIdentifier, queryD1 } from "@/lib/d1";
import { fetchB2Object } from "@/lib/b2";

export const runtime = "nodejs";

export async function GET(_request: Request, { params }: { params: { bookId: string } }) {
  const publicId = isNewBookIdentifier(params.bookId) ? getNewBookPublicId(params.bookId) : null;
  if (!publicId) return new NextResponse("Not found", { status: 404 });
  const rows = await queryD1<{ cover_url?: string | null }>("SELECT cover_url FROM books WHERE public_id = ? LIMIT 1", [publicId], 30 * 24 * 60 * 60);
  const coverUrl = rows[0]?.cover_url;
  if (!coverUrl?.startsWith("b2://")) return new NextResponse("Not found", { status: 404 });
  const object = await fetchB2Object(coverUrl);
  if (!object) return new NextResponse("Cover unavailable", { status: 502 });
  return new NextResponse(object.body as BodyInit, { headers: { "Content-Type": object.contentType, "Cache-Control": "public, max-age=2592000" } });
}
