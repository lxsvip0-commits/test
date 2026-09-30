#!/usr/bin/env python3
"""Import CSV/JSON records and render independent Markdown pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = ("title", "keyword", "summary", "body")
STYLES = {"guide", "overview", "update"}


def text(value):
    return str(value or "").strip()


def slugify(value):
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text(value).lower())
    return value.strip("-") or "page"


def url(value, name, row):
    value = text(value)
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError(f"第 {row} 条记录的 {name} 必须是完整的 http(s) URL")
    return value


def json_list(value, name, row):
    if not value:
        return []
    if isinstance(value, list):
        data = value
    else:
        try:
            data = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"第 {row} 条记录的 {name} 必须是 JSON 数组：{error.msg}") from error
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError(f"第 {row} 条记录的 {name} 必须是对象组成的 JSON 数组")
    return data


def load_records(path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file)), 2
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
        if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
            raise ValueError("JSON 文件顶层必须是页面对象数组")
        return records, 1
    raise ValueError("仅支持 .csv 或 .json 导入文件")


def list_section(title, values):
    entries = []
    for item in values:
        name, link, summary = text(item.get("title")), text(item.get("url")), text(item.get("summary"))
        if name and link:
            entries.append(f"- [{name}]({link})" + (f"：{summary}" if summary else ""))
    return f"## {title}\n\n" + "\n".join(entries) + "\n\n" if entries else ""


def content_fingerprint(page):
    """Stable hash for detecting identical imported page content."""
    fields = {
        "keyword": page["keyword"], "summary": page["summary"], "body": page["body"],
        "image": page["image"], "source_url": page["source_url"], "cta_label": page["cta_label"],
        "cta_url": page["cta_url"], "markers": page["markers"], "news": page["news"],
        "related": page["related"],
    }
    payload = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def similarity_profile(page):
    """Keep only imported, page-specific fields for future similarity checks."""
    related = page["news"] + page["related"]
    related_text = " ".join(
        f"{text(item.get('title'))} {text(item.get('summary'))}" for item in related
    )
    profile = "\n".join([
        page["title"], page["keyword"], page["summary"], page["body"],
        " ".join(page["markers"]), related_text,
    ])
    return re.sub(r"\s+", "", profile).lower()


def content_difference(first, second):
    """Return the different-content ratio: 0.0 is identical, 1.0 is unrelated."""
    return 1 - SequenceMatcher(None, first, second, autojunk=False).ratio()


def title_key(page):
    return re.sub(r"\s+", "", page["title"]).lower()


def render(page):
    escaped_title = page["title"].replace('"', "'")
    frontmatter = "\n".join([
        "---", f'title: "{escaped_title}"', f'keyword: "{page["keyword"]}"',
        f'slug: "{page["slug"]}"', f'source_id: "{page["source_id"]}"',
        f'published_at: "{page["published_at"]}"',
        f'updated_at: "{page["updated_at"]}"', f'style: "{page["style"]}"', "---", "",
    ])
    image = f"![{page['title']}]({page['image']})\n\n" if page["image"] else ""
    markers = "、".join(page["markers"]) or page["keyword"]
    source = f"资料来源：[查看原始资料]({page['source_url']})\n\n" if page["source_url"] else ""
    if page["style"] == "guide":
        body = f"# {page['title']}\n\n{image}{page['summary']}\n\n## 本文要点\n\n{markers}\n\n## 使用说明\n\n{page['body']}\n\n{source}"
    elif page["style"] == "update":
        body = f"# {page['title']}\n\n{image}> {page['summary']}\n\n## 本次更新\n\n{page['body']}\n\n## 适用范围\n\n{markers}\n\n{source}"
    else:
        body = f"# {page['title']}\n\n{image}{page['summary']}\n\n## 内容介绍\n\n{page['body']}\n\n## 相关标签\n\n{markers}\n\n{source}"
    cta = f"[ {page['cta_label']} ]({page['cta_url']})\n" if page["cta_label"] and page["cta_url"] else ""
    return frontmatter + body + "\n\n" + list_section("相关推荐", page["related"]) + list_section("相关资讯", page["news"]) + cta


def normalize(record, row, seen):
    missing = [name for name in REQUIRED if not text(record.get(name))]
    if missing:
        raise ValueError(f"第 {row} 条记录缺少必填字段：{', '.join(missing)}")
    style = text(record.get("style")) or "overview"
    if style not in STYLES:
        raise ValueError(f"第 {row} 条记录的 style 只能是 guide、overview 或 update")
    slug = slugify(record.get("slug") or record["title"])
    if slug in seen:
        raise ValueError(f"第 {row} 条记录的 slug 重复：{slug}")
    seen.add(slug)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "title": text(record["title"]), "keyword": text(record["keyword"]),
        "summary": text(record["summary"]), "body": text(record["body"]),
        "style": style, "slug": slug, "source_id": text(record.get("source_id")) or slug,
        "published_at": text(record.get("published_at")) or now,
        "updated_at": text(record.get("updated_at")) or now,
        "image": url(record.get("image"), "image", row),
        "source_url": url(record.get("source_url"), "source_url", row),
        "cta_label": text(record.get("cta_label")),
        "cta_url": url(record.get("cta_url"), "cta_url", row),
        "markers": [item.strip() for item in text(record.get("markers")).split(",") if item.strip()],
        "news": json_list(record.get("news_json"), "news_json", row),
        "related": json_list(record.get("related_json"), "related_json", row),
    }


def main():
    parser = argparse.ArgumentParser(description="把 CSV/JSON 数据批量生成 Markdown 页面")
    parser.add_argument("--input", required=True, type=Path, help="CSV 或 JSON 导入文件")
    parser.add_argument("--output", type=Path, default=Path("generated"), help="输出目录")
    parser.add_argument(
        "--min-difference", type=float, default=0.50,
        help="新页面与已有页面的最小内容差异率，默认 0.50（即至少 50%% 不同）",
    )
    args = parser.parse_args()
    if not 0 <= args.min_difference <= 1:
        parser.error("--min-difference 必须介于 0 和 1 之间")
    try:
        records, start_row = load_records(args.input)
        if not records:
            raise ValueError("导入文件没有页面数据")
        seen = set()
        pages = [normalize(item, start_row + index, seen) for index, item in enumerate(records)]
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"导入失败：{error}", file=sys.stderr)
        return 1

    output = args.output.resolve()
    manifest_file = output / "manifest.json"
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else []
        if not isinstance(manifest, list):
            raise ValueError("manifest.json 必须是页面对象数组")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"无法读取现有清单：{error}", file=sys.stderr)
        return 1

    by_source = {text(item.get("source_id")) or text(item.get("slug")): item for item in manifest}
    by_fingerprint = {text(item.get("fingerprint")): item for item in manifest if text(item.get("fingerprint"))}
    by_title = {text(item.get("title_key")): item for item in manifest if text(item.get("title_key"))}
    seen_sources, seen_fingerprints, seen_titles = set(), set(), set()
    profiles = [(item, text(item.get("comparison_text"))) for item in manifest if text(item.get("comparison_text"))]
    created = updated = skipped = 0

    for page in pages:
        source_id = page["source_id"]
        fingerprint = content_fingerprint(page)
        key = title_key(page)
        profile = similarity_profile(page)
        if source_id in seen_sources:
            print(f"跳过重复 source_id：{source_id}")
            skipped += 1
            continue
        if fingerprint in seen_fingerprints or key in seen_titles:
            print(f"跳过导入文件中的重复页面：{page['title']}")
            skipped += 1
            continue
        seen_sources.add(source_id)
        seen_fingerprints.add(fingerprint)
        seen_titles.add(key)

        existing = by_source.get(source_id)
        duplicate = by_fingerprint.get(fingerprint) or by_title.get(key)
        if not existing and duplicate:
            print(f"跳过已存在的重复页面：{page['title']}")
            skipped += 1
            continue
        if existing and existing.get("fingerprint") == fingerprint:
            if not existing.get("comparison_text"):
                existing["comparison_text"] = profile
                profiles.append((existing, profile))
            print(f"跳过未变化页面：{page['title']}")
            skipped += 1
            continue

        if not existing:
            conflict = None
            for item, other_profile in profiles:
                difference = content_difference(profile, other_profile)
                if difference < args.min_difference:
                    conflict = (item, difference)
                    break
            if conflict:
                item, difference = conflict
                print(
                    f"跳过相似页面：{page['title']} 与 {item.get('title', item.get('slug'))} 的差异仅 "
                    f"{difference:.1%}，低于 {args.min_difference:.0%}"
                )
                skipped += 1
                continue

        relative = Path(existing["path"]) if existing and existing.get("path") else Path(page["published_at"][:4]) / page["published_at"][5:7] / f"{page['slug']}.md"
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render(page), encoding="utf-8")
        if existing:
            old_fingerprint = text(existing.get("fingerprint"))
            old_title_key = text(existing.get("title_key"))
            if by_fingerprint.get(old_fingerprint) is existing:
                del by_fingerprint[old_fingerprint]
            if by_title.get(old_title_key) is existing:
                del by_title[old_title_key]
            profiles = [(item, old_profile) for item, old_profile in profiles if item is not existing]
        entry = {
            "source_id": source_id, "title": page["title"], "title_key": key,
            "slug": page["slug"], "path": relative.as_posix(), "fingerprint": fingerprint,
            "updated_at": page["updated_at"], "comparison_text": profile,
        }
        by_source[source_id] = entry
        by_fingerprint[fingerprint] = entry
        by_title[key] = entry
        profiles.append((entry, profile))
        if existing:
            updated += 1
        else:
            created += 1

    output.mkdir(parents=True, exist_ok=True)
    final_manifest = sorted(by_source.values(), key=lambda item: item["path"])
    manifest_file.write_text(json.dumps(final_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成：新增 {created}，更新 {updated}，跳过 {skipped}；输出目录：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
