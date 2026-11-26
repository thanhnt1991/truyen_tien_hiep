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
  return process.env.NODE_ENV !== "development";
}

function maintenanceResponse(request: NextRequest) {
  const headers = { "Cache-Control": "no-store, max-age=0" };
  const fallbackUrl = "https://tienhiepvn.vercel.app/";

  if (request.nextUrl.pathname.startsWith("/api/")) {
    return NextResponse.json(
      {
        error: "Website hiện đang được bảo trì. Vui lòng đọc truyện tại web dự phòng.",
        fallbackUrl,
      },
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
      a { color: #1769aa; font-weight: 600; text-underline-offset: 3px; }
      .ad { margin: 24px auto 0; width: 300px; max-width: 100%; }
      .ad-label { display: block; margin-bottom: 4px; color: #A09688; font-size: 10px; letter-spacing: .08em; text-transform: uppercase; }
      .ad-slot { width: 300px; height: 250px; max-width: 100%; overflow: hidden; display: flex; align-items: center; justify-content: center; background: rgba(244,239,230,.5); border: 1px solid rgba(230,216,189,.5); border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
    </style>
  </head>
  <body>
    <main>
      <h1>Tiên Hiệp Lâu đang bảo trì</h1>
      <p>Website hiện đang được bảo trì. Vui lòng đọc truyện tại web dự phòng <a href="${fallbackUrl}" rel="noopener noreferrer">tienhiepvn.vercel.app</a>.</p>
      <div class="ad">
        <span class="ad-label">Quảng cáo</span>
        <div id="maintenance-ad-slot" class="ad-slot"></div>
      </div>
    </main>
    <script>
      window.addEventListener("load", function () {
        var slot = document.getElementById("maintenance-ad-slot");
        if (!slot) return;
        window.atOptions = {
          key: "7e0c3d059c2e2a6efdb2dcbf740c0940",
          format: "iframe",
          height: 250,
          width: 300,
          params: {}
        };
        var script = document.createElement("script");
        script.src = "https://www.highrevenueformat.com/7e0c3d059c2e2a6efdb2dcbf740c0940/invoke.js";
        script.async = true;
        slot.appendChild(script);
      }, { once: true });
    </script>
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
