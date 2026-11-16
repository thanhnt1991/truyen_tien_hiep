"use client";

import { useState } from "react";
import { getCoverUrl } from "@/lib/covers";

export default function SuggestedCover({
  id,
  title,
  coverUrl,
  small = false,
}: {
  id: number | string;
  title: string;
  coverUrl: string;
  small?: boolean;
}) {
  const [failed, setFailed] = useState(false);
  const classes = small
    ? "h-12 w-8 shrink-0 rounded-sm text-[8px]"
    : "aspect-[2/3] w-full rounded-md text-xs";

  if (failed || !coverUrl) {
    return (
      <span className={`flex items-center justify-center overflow-hidden border border-[#DDD5C8] bg-[#E9DFC9] p-1 text-center font-serif-reading font-semibold leading-tight text-[#6B5638] ${classes}`} aria-label={`Không tải được bìa ${title}`}>
        {small ? "Truyện" : title}
      </span>
    );
  }

  return (
    <img
      src={getCoverUrl(id, coverUrl)}
      alt={small ? "" : `Bìa ${title}`}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
      className={`border border-[#DDD5C8] bg-[#EFE9DC] object-cover ${classes}`}
    />
  );
}
