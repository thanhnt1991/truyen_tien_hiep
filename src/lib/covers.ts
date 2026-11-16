export function getCoverUrl(id: number | string, coverUrl?: string | null) {
  if (!coverUrl) return "";
  return coverUrl.startsWith("b2://") ? `/api/covers/${encodeURIComponent(String(id))}` : coverUrl;
}
