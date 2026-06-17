#!/usr/bin/env python3
"""Fetch and summarize the latest Jike feed posts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any


ROW_KEYS = {"id", "author", "content", "time", "url"}
WRAPPER_KEYS = ("data", "items", "results", "rows", "list")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group latest Jike feed entries by author."
    )
    parser.add_argument("--limit", type=int, default=30, help="Posts requested from OpenCLI.")
    parser.add_argument("--opencli", default="opencli", help="Path to the opencli executable.")
    parser.add_argument(
        "--input",
        action="append",
        type=Path,
        help="Read JSON from a file instead of OpenCLI. Repeat for multiple files.",
    )
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    return args


def extract_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        rows = [item for item in value if isinstance(item, dict)]
        if rows and any(ROW_KEYS.intersection(row) for row in rows):
            return rows
        for item in value:
            found = extract_rows(item)
            if found:
                return found
        return []

    if isinstance(value, dict):
        if ROW_KEYS.intersection(value):
            return [value]
        for key in WRAPPER_KEYS:
            if key in value:
                found = extract_rows(value[key])
                if found:
                    return found
        for child in value.values():
            found = extract_rows(child)
            if found:
                return found
    return []


def read_json(text: str, source: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{source} did not return valid JSON: {exc}") from exc
    return extract_rows(payload)


def fetch_feed(executable: str, limit: int) -> list[dict[str, Any]]:
    command = [executable, "jike", "feed", "-f", "json", "--limit", str(limit)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or "OpenCLI failed while fetching Jike feed")
    return read_json(result.stdout, "OpenCLI")


def scalar_text(value: Any, candidates: tuple[str, ...] = ()) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in candidates:
            if key in value:
                text = scalar_text(value[key])
                if text:
                    return text
    return ""


def display_time(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, (int, float)):
        stamp = float(value)
        if stamp > 10_000_000_000:
            stamp /= 1000
        try:
            return datetime.fromtimestamp(stamp).astimezone().strftime("%H:%M")
        except (OverflowError, OSError, ValueError):
            return scalar_text(value)

    text = scalar_text(value)
    if not text:
        return ""

    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.astimezone().strftime("%H:%M") if parsed.tzinfo else parsed.strftime("%H:%M")
    except ValueError:
        return text


def markdown_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


def summarize(rows: list[dict[str, Any]]) -> str:
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in rows:
        post_id = scalar_text(row.get("id"))
        url = scalar_text(row.get("url"), ("url", "link", "href"))
        identity = post_id or url or json.dumps(row, ensure_ascii=False, sort_keys=True)
        if identity in seen:
            continue
        seen.add(identity)

        author = scalar_text(row.get("author"), ("name", "screenName", "username")) or "未知作者"
        content = scalar_text(row.get("content"), ("text", "title", "body")) or "无内容"
        posts.append({
            "author": author,
            "content": content,
            "url": url,
            "time": display_time(row.get("time")),
            "time_raw": row.get("time") or "",
        })

    if not posts:
        return "没有检测到即刻动态。"

    # 按时间倒序排列（最新的在前）
    def time_sort_key(p: dict[str, Any]) -> str:
        return str(p.get("time_raw", ""))
    posts.sort(key=time_sort_key, reverse=True)

    output = ["| 作者 | 内容 | 时间 |", "|---|---|---|"]
    for post in posts:
        link = f"<{post['url']}>" if post["url"] else ""
        content_cell = f"{markdown_text(post['content'])}，{link}" if link else markdown_text(post["content"])
        output.append(
            f"| {markdown_text(post['author'])} | {content_cell} | {post['time']} |"
        )
    return "\n".join(output)


def main() -> int:
    args = parse_args()
    try:
        if args.input:
            rows = []
            for path in args.input:
                rows.extend(read_json(path.read_text(encoding="utf-8"), str(path)))
        else:
            rows = fetch_feed(args.opencli, args.limit)
        print(summarize(rows))
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
