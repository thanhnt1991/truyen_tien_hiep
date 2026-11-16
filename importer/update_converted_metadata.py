#!/usr/bin/env python3
"""Generate resumable SEO metadata for converted book folders using Gemini."""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import batch_epub_upload as batch


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BOOKS_DIR = SCRIPT_DIR / "chapters"
DEFAULT_STATE = SCRIPT_DIR / "converted_metadata_state_2026-10-17.json"


def read_info(path: Path) -> tuple[dict[str, str], list[str]]:
    info: dict[str, str] = {}
    other_lines: list[str] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" not in line:
                other_lines.append(line)
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key in {"title", "author", "status", "source_type", "ranking", "genres", "description"}:
                info[key] = value.strip()
            else:
                other_lines.append(line)
    return info, other_lines


def chapter_context(book_dir: Path, ending: bool, limit: int) -> str:
    paths = batch.list_chapter_paths(book_dir)
    if not paths:
        return ""
    path = paths[-1] if ending else paths[0]
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    text = batch.clean_text(text)
    if ending:
        text = text[-limit:]
    return text[:limit]


def request_metadata(title: str, author: str, first: str, ending: str, chapter_count: int,
                     api_key: str, model: str, timeout: int) -> dict:
    prompt = f"""Bạn là biên tập viên metadata cho thư viện truyện tiếng Việt. Chỉ căn cứ nội dung trích dẫn, không suy diễn từ tên truyện.
Tác phẩm: {title}
Tác giả: {author}
Số file chương: {chapter_count}

Trích đoạn đầu:
---
{first}
---
Trích đoạn cuối của chương cuối:
---
{ending}
---

Trả về JSON theo schema, không thêm văn bản ngoài JSON.
- description: tiếng Việt tự nhiên, khoảng 70-110 từ, mô tả tổng quan có căn cứ từ các trích đoạn; nêu tên truyện/tác giả, không bịa tình tiết, không dùng câu quảng cáo chung chung.
- genres: đúng 5 tag SEO, mỗi tag đúng 2 từ tiếng Việt; mô tả thể loại/chủ đề có căn cứ, không lặp tag, không mặc định tiên hiệp.
- status: chỉ "Hoàn thành" hoặc "Đang ra". Chỉ ghi Đang ra khi chương cuối cho thấy rõ mạch truyện còn tiếp diễn/chưa kết thúc. Nếu không chắc, ghi Hoàn thành.
- confidence: "high", "medium" hoặc "low"; mức thấp vẫn dùng status Hoàn thành theo quy tắc trên.
"""
    schema = {
        "type": "OBJECT",
        "properties": {
            "description": {"type": "STRING"},
            "genres": {"type": "ARRAY", "minItems": 5, "maxItems": 5, "items": {"type": "STRING"}},
            "status": {"type": "STRING", "enum": ["Hoàn thành", "Đang ra"]},
            "confidence": {"type": "STRING", "enum": ["high", "medium", "low"]},
        },
        "required": ["description", "genres", "status", "confidence"],
    }
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 700,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            output = "".join(
                part.get("text", "")
                for part in payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            )
            result = json.loads(output)
            description = batch.clean_text(result.get("description", ""))
            genres = [batch.normalize_keyword(str(tag)) for tag in result.get("genres", [])]
            if (len(description.split()) < 40 or len(genres) != 5
                    or any(len(tag.split()) != 2 for tag in genres)
                    or len({tag.casefold() for tag in genres}) != 5):
                raise ValueError("AI metadata không đạt yêu cầu (description/tag) .")
            if result.get("status") not in {"Hoàn thành", "Đang ra"}:
                raise ValueError("Status không hợp lệ.")
            if result.get("confidence") not in {"high", "medium", "low"}:
                raise ValueError("Confidence không hợp lệ.")
            return {"description": description, "genres": genres,
                    "status": result["status"], "confidence": result["confidence"]}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            if exc.code == 429 and attempt < 3:
                delay = 30 * (attempt + 1)
                print(f"  ⏳ Gemini rate limit, chờ {delay}s rồi thử lại.", flush=True)
                time.sleep(delay)
                continue
            raise RuntimeError(f"Gemini HTTP {exc.code}: {detail}") from exc
    raise RuntimeError("Gemini hết số lần thử.")


def save_book_info(path: Path, info: dict[str, str], other_lines: list[str], metadata: dict) -> None:
    updated = dict(info)
    updated.setdefault("title", path.parent.name.removesuffix("_Translated").replace("_", " "))
    updated.setdefault("author", "Chưa rõ")
    updated.setdefault("ranking", "")
    updated["status"] = metadata["status"]
    updated.setdefault("source_type", "Convert")
    updated["genres"] = ", ".join(metadata["genres"])
    updated["description"] = metadata["description"]
    order = ["title", "author", "status", "source_type", "ranking", "genres", "description"]
    content = "\n".join(f"{key}={updated.get(key, '')}" for key in order)
    if other_lines:
        content += "\n" + "\n".join(other_lines)
    tmp = path.with_suffix(".txt.tmp")
    tmp.write_text(content + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv(SCRIPT_DIR / ".env")
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description="Update status, description and 5 SEO tags for converted stories.")
    parser.add_argument("--books-dir", type=Path, default=DEFAULT_BOOKS_DIR)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", batch.DEFAULT_GEMINI_MODEL))
    parser.add_argument("--delay", type=float, default=5)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Thiếu GEMINI_API_KEY trong importer/.env", file=sys.stderr)
        return 2
    books = sorted(p for p in args.books_dir.glob("*_Translated") if p.is_dir())
    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {"completed": {}, "failed": {}}
    completed = state.setdefault("completed", {})
    failed = state.setdefault("failed", {})
    pending = [book for book in books if book.name not in completed]
    if args.limit is not None:
        pending = pending[:args.limit]
    print(f"📚 Tổng folder: {len(books)}; đã xong checkpoint: {len(completed)}; lượt này: {len(pending)}")

    for index, book_dir in enumerate(pending, 1):
        info_path = book_dir / "book_info.txt"
        info, other_lines = read_info(info_path)
        title = batch.clean_text(info.get("title", ""), book_dir.name.removesuffix("_Translated").replace("_", " "))
        author = batch.clean_text(info.get("author", ""), "Chưa rõ")
        chapters = batch.list_chapter_paths(book_dir)
        if not chapters:
            failed[book_dir.name] = "Không có file chương Markdown"
            print(f"[{index}/{len(pending)}] ⚠️ {book_dir.name}: không có chapter .md", flush=True)
            continue
        print(f"[{index}/{len(pending)}] {title} ({len(chapters)} chương)", flush=True)
        try:
            metadata = request_metadata(title, author, chapter_context(book_dir, False, 1800),
                                        chapter_context(book_dir, True, 2600), len(chapters),
                                        api_key, args.model, args.timeout)
            save_book_info(info_path, info, other_lines, metadata)
            completed[book_dir.name] = {
                "status": metadata["status"], "confidence": metadata["confidence"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            failed.pop(book_dir.name, None)
            print(f"  ✅ {metadata['status']} ({metadata['confidence']}), 5 tag; đã lưu book_info", flush=True)
        except Exception as exc:
            failed[book_dir.name] = str(exc)
            print(f"  ❌ Lỗi: {exc}", flush=True)
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if index < len(pending) and args.delay:
            time.sleep(args.delay)

    print(f"Kết quả lượt này: {len(completed)}/{len(books)} hoàn tất; {len(failed)} lỗi/thiếu chương.")
    print(f"Checkpoint: {args.state}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
