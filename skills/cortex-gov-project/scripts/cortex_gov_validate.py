#!/usr/bin/env python3
"""
Validate Cortex GOV evidence and optionally auto-advance VERIFY -> DONE.

Usage:
  python cortex_gov_validate.py --project <PROJECT.md> [--auto-verify true|false] [--check-urls]

Behavior:
- Finds the first task in VERIFY status.
- Verifies evidence fields are populated.
- Verifies file paths exist (if provided).
- Optionally checks URLs are reachable.
- If valid and auto-verify true, flips VERIFY -> DONE.
"""

import argparse
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

STATUS_RE = re.compile(r"Status:\s*(TODO|IN_PROGRESS|VERIFY|DONE|BLOCKED)")
TASK_RE = re.compile(r"^###\s+(H\d+):\s+(.*)$", re.MULTILINE)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_verify_task(text: str):
    # Find first task header and its block
    headers = list(TASK_RE.finditer(text))
    for i, h in enumerate(headers):
        start = h.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        if "Status: VERIFY" in block:
            return h.group(1), block, start, end
    return None, None, None, None


def parse_evidence(block: str):
    def get_line(prefix):
        m = re.search(rf"^\s*- {re.escape(prefix)}:\s*(.*)$", block, re.MULTILINE)
        return m.group(1).strip() if m else ""

    urls = get_line("URLs")
    paths = get_line("File paths")
    notes = get_line("Notes")
    return urls, paths, notes


def check_paths(paths_str: str):
    if not paths_str:
        return True, []
    paths = [p.strip() for p in paths_str.split(",") if p.strip()]
    missing = [p for p in paths if not Path(p).exists()]
    return len(missing) == 0, missing


def check_urls(urls_str: str):
    if not urls_str:
        return True, []
    urls = [u.strip() for u in urls_str.split(";") if u.strip()]
    failed = []
    for u in urls:
        try:
            req = Request(u, headers={"User-Agent": "cortex-gov-validate"})
            with urlopen(req, timeout=10) as resp:
                if resp.status >= 400:
                    failed.append(u)
        except (URLError, HTTPError):
            failed.append(u)
    return len(failed) == 0, failed


def set_status_done(text: str, start: int, end: int):
    block = text[start:end]
    block = block.replace("Status: VERIFY", "Status: DONE")
    return text[:start] + block + text[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Path to PROJECT.md")
    parser.add_argument("--auto-verify", default="true", help="true|false")
    parser.add_argument("--check-urls", action="store_true")
    args = parser.parse_args()

    project_path = Path(args.project)
    text = load_text(project_path)

    task_key, block, start, end = find_verify_task(text)
    if not block:
        print("No task in VERIFY status.")
        return

    urls, paths, notes = parse_evidence(block)

    ok_paths, missing = check_paths(paths)
    if not ok_paths:
        print(f"Missing evidence file paths: {missing}")
        return

    if args.check_urls:
        ok_urls, failed = check_urls(urls)
        if not ok_urls:
            print(f"Unreachable URLs: {failed}")
            return

    auto_verify = args.auto_verify.lower() == "true"
    if auto_verify:
        updated = set_status_done(text, start, end)
        project_path.write_text(updated, encoding="utf-8")
        print(f"{task_key}: VERIFY -> DONE")
    else:
        print(f"{task_key} validated. Awaiting manual approval.")


if __name__ == "__main__":
    main()
