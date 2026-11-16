import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const ALLOWED_SEARCH_BOTS = [
  "googlebot",
  "bingbot",
  "slurp",
  "duckduckbot",
  "baiduspider",
  "yandexbot",
  "coccocbot",
];

const BLOCKED_BOTS = [
  "ahrefsbot",
  "semrushbot",
  "mj12bot",
  "dotbot",
  "petalbot",
  "bytespider",
  "claudebot",
  "gptbot",
  "ccbot",
  "amazonbot",
  "dataforseobot",
  "barkrowler",
  "blexbot",
  "seekportbot",
  "serpstatbot",
  "seznambot",
  "megaindex",
  "scrapy",
  "python-requests",
  "go-http-client",
  "wget",
  "curl",
];

function includesAny(value: string, needles: string[]) {
  return needles.some((needle) => value.includes(needle));
}

function isMaintenanceWindow() {
  const hour = (new Date().getUTCHours() + 7) % 24;
  return hour >= 2 && hour < 5;
}

function maintenanceResponse(request: NextRequest) {
  const headers = { "Cache-Control": "no-store, max-age=0" };

  if (request.nextUrl.pathname.startsWith("/api/")) {
    return NextResponse.json(
      { error: "Website đang bảo trì, vui lòng quay lại sau 5:00 AM." },
      { status: 503, headers },
    );
  }

  return new NextResponse(
    `<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">
    <title>Đang bảo trì | Tiên Hiệp Lâu</title>
    <style>
      * { box-sizing: border-box; }
      body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; background: #f7f4ed; color: #2c2825; font-family: system-ui, sans-serif; }
      main { width: min(100%, 520px); padding: 36px 28px; text-align: center; border: 1px solid #d8cdbb; border-radius: 12px; background: #fffdf8; box-shadow: 0 12px 36px rgba(66, 52, 35, .08); }
      h1 { margin: 0 0 12px; font-family: Georgia, serif; font-size: 28px; }
      p { margin: 0; color: #6b6357; font-size: 15px; line-height: 1.7; }
    </style>
  </head>
  <body>
    <main>
      <h1>Tiên Hiệp Lâu đang bảo trì</h1>
      <p>Website đang bảo trì, vui lòng quay lại sau 5:00 AM.</p>
    </main>
  </body>
</html>`,
    {
      status: 503,
      headers: {
        ...headers,
        "Content-Type": "text/html; charset=utf-8",
      },
    },
  );
}

export function middleware(request: NextRequest) {
  if (isMaintenanceWindow()) {
    return maintenanceResponse(request);
  }

  const userAgent = (request.headers.get("user-agent") || "").toLowerCase();

  if (includesAny(userAgent, ALLOWED_SEARCH_BOTS)) {
    return NextResponse.next();
  }

  if (includesAny(userAgent, BLOCKED_BOTS)) {
    return new NextResponse("Forbidden", {
      status: 403,
      headers: {
        "Cache-Control": "public, max-age=3600",
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/books/:path*",
    "/api/:path*",
    "/sitemap.xml",
  ],
};
