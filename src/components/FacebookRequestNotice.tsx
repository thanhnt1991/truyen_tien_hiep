const facebookGroupUrl = "https://www.facebook.com/share/g/19f1cTZMUR/";

interface FacebookRequestNoticeProps {
  compact?: boolean;
}

export default function FacebookRequestNotice({ compact = false }: FacebookRequestNoticeProps) {
  return (
    <section
      aria-labelledby="facebook-request-title"
      className={compact
        ? "w-full max-w-[420px] rounded-md border border-[#C69C4E]/45 bg-[#FFF8E8] px-3 py-3 shadow-[0_4px_14px_rgba(138,106,45,0.08)]"
        : "border-y border-x border-[#C69C4E]/35 bg-[#FFF8E8] px-4 py-4"
      }
    >
      <div className={compact ? "flex flex-col gap-2" : "flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"}>
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#9A6A20]">
            Cộng đồng Tiên Hiệp Lâu
          </p>
          <h2 id="facebook-request-title" className="mt-1 text-sm font-semibold text-[#2C2825]">
            Bạn muốn đọc truyện nào tiếp theo?
          </h2>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-[#6B6357]">
            Gửi yêu cầu truyện mới hoặc chương còn thiếu trong nhóm Facebook để mọi người cùng hỗ trợ.
          </p>
        </div>

        <a
          href={facebookGroupUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex shrink-0 items-center justify-center rounded-md bg-[#2563A6] px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-[#1E4F86] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#7EA9D3] focus-visible:ring-offset-2"
        >
          Gửi yêu cầu vào nhóm Facebook
        </a>
      </div>
    </section>
  );
}
