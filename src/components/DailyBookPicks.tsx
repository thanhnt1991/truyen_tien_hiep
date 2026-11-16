import Link from "next/link";
import { getBookPath } from "@/lib/seo";
import SuggestedCover from "@/components/SuggestedCover";

interface SuggestedBook {
  id: number | string;
  title: string;
  author: string;
  chapterCount: number;
  description: string;
  coverUrl: string;
}

export default function DailyBookPicks({ books }: { books: SuggestedBook[] }) {
  const [featured, ...others] = books;
  if (!featured) return null;

  return (
    <section aria-labelledby="daily-books-title" className="rounded-lg border border-[#D8CDBB] bg-[#FBFAF7] p-4 shadow-[0_5px_22px_rgba(66,52,35,0.05)] md:p-5">
      <div className="mb-4 flex items-center gap-3">
        <span className="h-7 w-1 rounded-full bg-[#B99654]" aria-hidden="true" />
        <div>
          <h2 id="daily-books-title" className="font-serif-reading text-lg font-bold text-[#2C2825]">Truyện gợi ý</h2>
          <p className="text-xs text-[#7A7365]">Khám phá những bộ truyện bạn có thể đã bỏ lỡ</p>
        </div>
      </div>

      <div className="flex gap-4 border-b border-[#E8E0D2] pb-4 md:gap-5">
        <Link href={getBookPath(featured)} className="w-28 shrink-0 self-start overflow-hidden rounded-md border border-[#D8CDBB] bg-[#EFE9DC] sm:w-32 md:w-36">
          <SuggestedCover key={featured.id} id={featured.id} title={featured.title} coverUrl={featured.coverUrl} />
        </Link>
        <div className="min-w-0 flex-1">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-[#947038]">Truyện tiêu biểu</p>
          <Link href={getBookPath(featured)} className="font-serif-reading text-lg font-bold leading-snug text-[#2C2825] hover:text-[#8A6828] md:text-xl">
            {featured.title}
          </Link>
          <p className="mt-1 text-xs text-[#7A7365]">{featured.author} · {featured.chapterCount} chương</p>
          <p className="mt-3 line-clamp-4 whitespace-pre-line text-sm leading-6 text-[#5E5448] md:line-clamp-5">
            {featured.description || "Chưa có mô tả cho truyện này."}
          </p>
          <Link href={getBookPath(featured)} className="mt-3 inline-block text-xs font-semibold text-[#8A6828] hover:underline">
            Xem truyện →
          </Link>
        </div>
      </div>

      {others.length > 0 && (
        <div className="pt-3">
          <p className="mb-2 text-xs font-semibold text-[#6B6357]">Có thể bạn sẽ thích</p>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {others.map((book) => (
              <Link key={book.id} href={getBookPath(book)} className="flex min-w-0 items-center gap-2 rounded-md p-1.5 transition-colors hover:bg-[#F1ECE2]">
                <SuggestedCover id={book.id} title={book.title} coverUrl={book.coverUrl} small />
                <span className="line-clamp-2 text-xs font-semibold leading-snug text-[#3B332A]">{book.title}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
