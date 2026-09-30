#!/usr/bin/env python3
"""Render Markdown pages from fixed, batch, and page-level JSON data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


PLACEHOLDER = re.compile(r"{{([A-Z][A-Z0-9_]*)}}")


def load_object(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"无法读取 {path}：{error}") from error
    if not isinstance(data, dict) or not all(isinstance(key, str) for key in data):
        raise ValueError(f"{path} 必须是 JSON 对象")
    return {key: "" if value is None else str(value) for key, value in data.items()}


def valid_optional_url(value: str, field: str, source: Path) -> None:
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError(f"{source} 的 {field} 必须是完整的 http(s) URL")


def render(template: str, values: dict[str, str], page_path: Path) -> str:
    missing = sorted(set(PLACEHOLDER.findall(template)) - set(values))
    if missing:
        raise ValueError(f"{page_path} 缺少模板字段：{', '.join(missing)}")
    valid_optional_url(values.get("IMAGE_URL", ""), "IMAGE_URL", page_path)
    valid_optional_url(values.get("TARGET_URL", ""), "TARGET_URL", page_path)
    output = PLACEHOLDER.sub(lambda match: values[match.group(1)], template)
    output = re.sub(r"^!\[[^\]]*\]\(\)\s*\n", "", output, flags=re.MULTILINE)
    output = re.sub(r"^\[[^\]]*\]\(\)\s*\n", "", output, flags=re.MULTILINE)
    return re.sub(r"\n{3,}", "\n\n", output).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="按三级 JSON 标签渲染 Markdown 页面")
    parser.add_argument("--template", type=Path, default=Path("template.md"))
    parser.add_argument("--site", type=Path, default=Path("data/site.json"))
    parser.add_argument("--jobs", type=Path, default=Path("data/render-jobs.json"))
    parser.add_argument("--output", type=Path, default=Path("generated"))
    args = parser.parse_args()
    try:
        template = args.template.read_text(encoding="utf-8")
        site = load_object(args.site)
        jobs = json.loads(args.jobs.read_text(encoding="utf-8"))
        if not isinstance(jobs, list) or not jobs:
            raise ValueError(f"{args.jobs} 必须是非空 JSON 数组")
        created: list[Path] = []
        for index, job in enumerate(jobs, start=1):
            if not isinstance(job, dict):
                raise ValueError(f"{args.jobs} 第 {index} 项必须是对象")
            page_file = Path(str(job.get("page", "")))
            batch_file = Path(str(job.get("batch", "")))
            relative_output = Path(str(job.get("output", "")))
            if not page_file or not batch_file or not str(relative_output):
                raise ValueError(f"{args.jobs} 第 {index} 项需要 page、batch 和 output")
            if relative_output.is_absolute() or ".." in relative_output.parts:
                raise ValueError(f"{args.jobs} 第 {index} 项的 output 必须是相对安全路径")
            values = {**site, **load_object(batch_file), **load_object(page_file)}
            destination = args.output / relative_output
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(render(template, values, page_file), encoding="utf-8")
            created.append(destination)
    except ValueError as error:
        print(f"渲染失败：{error}", file=sys.stderr)
        return 1
    print(f"完成：已渲染 {len(created)} 个页面")
    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
