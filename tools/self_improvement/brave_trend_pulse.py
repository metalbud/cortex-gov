"""H013 Brave trend pulse for recursive planning context.

Runs Brave web search queries before each recursive planning cycle and stores:
- a Markdown summary for humans
- append-only JSON pulse log for auditability
- a planning-context JSON payload for downstream proposal generation
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_PATH = BASE_DIR / "PROJECT.md"
DEFAULT_SUMMARY_PATH = BASE_DIR / "artifacts" / "verification" / "H013-brave-trends.md"
DEFAULT_LOG_PATH = BASE_DIR / "artifacts" / "metrics" / "H013-brave-log.json"
DEFAULT_CONTEXT_PATH = BASE_DIR / "artifacts" / "metrics" / "H013-planning-context.json"

BRAVE_SEARCH_URL = "https://search.brave.com/search?q={query}"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

RESULT_RE = re.compile(
    r'title:"(?P<title>[^"\n]{5,220})",url:"(?P<url>https?://[^"\n]+)"'
    r'[^\n]{0,900}?description:"(?P<desc>[^"\n]{10,500})"',
    re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}")

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "your",
    "about",
    "how",
    "what",
    "when",
    "where",
    "which",
    "will",
    "are",
    "was",
    "were",
    "you",
    "our",
    "their",
    "while",
    "before",
    "after",
    "into",
    "agent",
    "agents",
    "governance",
    "recursive",
    "planning",
}

TOOL_TERMS = [
    "autogen",
    "langgraph",
    "crewai",
    "copilot",
    "openai",
    "anthropic",
    "claude",
    "mcp",
    "zapier",
    "n8n",
    "airflow",
    "prefect",
    "cursor",
    "windsurf",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json_array(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array.")
    return data


def parse_project_focus(project_path: Path) -> List[Dict[str, str]]:
    if not project_path.exists():
        return []
    text = project_path.read_text(encoding="utf-8")
    task_re = re.compile(
        r"### (?P<key>H\d+): (?P<title>.+?)\n"
        r"Epic: (?P<epic>E\d+)\n"
        r"Status: (?P<status>[A-Z_]+)\n"
        r"Priority: (?P<priority>P\d)",
        re.MULTILINE,
    )
    tasks: List[Dict[str, str]] = []
    for match in task_re.finditer(text):
        task = match.groupdict()
        if task["status"] in {"IN_PROGRESS", "TODO"}:
            tasks.append(task)
    priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda item: (priority_rank.get(item["priority"], 9), item["key"]))
    return tasks[:3]


def build_queries(project_focus: List[Dict[str, str]], extra_queries: List[str]) -> List[str]:
    base_queries = [
        "AI agent governance automation",
        "autonomous software development feedback loop 2026",
        "AI safety rails for autonomous coding agents",
    ]
    focus_queries = []
    for task in project_focus:
        focus_queries.append(f"{task['title']} tools trends 2026")
    merged = base_queries + focus_queries + extra_queries
    deduped: List[str] = []
    seen = set()
    for query in merged:
        norm = query.strip().lower()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        deduped.append(query.strip())
    return deduped[:5]


def clean_snippet(text: str) -> str:
    text = unescape(text)
    text = text.replace("\\u003C", "<").replace("\\u003E", ">")
    text = TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_domain(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.lower().removeprefix("www.")


def search_brave(query: str, max_results: int = 5) -> Dict:
    url = BRAVE_SEARCH_URL.format(query=quote_plus(query))
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=25) as response:
        html = response.read().decode("utf-8", errors="ignore")

    results: List[Dict[str, str]] = []
    seen_urls = set()
    for match in RESULT_RE.finditer(html):
        title = clean_snippet(match.group("title"))
        result_url = unescape(match.group("url"))
        snippet = clean_snippet(match.group("desc"))
        if result_url in seen_urls:
            continue
        seen_urls.add(result_url)
        results.append(
            {
                "title": title,
                "url": result_url,
                "snippet": snippet,
                "domain": extract_domain(result_url),
            }
        )
        if len(results) >= max_results:
            break

    return {"query": query, "searchUrl": url, "results": results}


def extract_keywords(results: List[Dict[str, str]]) -> Dict[str, List[str]]:
    token_counter: Counter[str] = Counter()
    tool_hits = set()
    competitor_counter: Counter[str] = Counter()
    for item in results:
        blob = f"{item['title']} {item['snippet']}".lower()
        for word in WORD_RE.findall(blob):
            if word in STOPWORDS:
                continue
            token_counter[word] += 1
        for term in TOOL_TERMS:
            if term in blob:
                tool_hits.add(term)
        domain = item.get("domain", "")
        if domain:
            competitor_counter[domain] += 1

    buzzwords = [word for word, _ in token_counter.most_common(12)]
    competitors = [domain for domain, _ in competitor_counter.most_common(8)]
    tools = sorted(tool_hits)
    return {"buzzwords": buzzwords, "competitors": competitors, "tools": tools}


def aggregate_signals(query_entries: List[Dict]) -> Dict[str, List[str]]:
    all_results = [result for entry in query_entries for result in entry.get("results", [])]
    return extract_keywords(all_results)


def render_summary_markdown(pulse: Dict) -> str:
    lines = [
        "# H013 Brave Trend Pulse",
        "",
        f"Generated: {pulse['capturedAt']}",
        f"Pulse ID: {pulse['pulseId']}",
        "",
        "## Cadence",
        "",
        "- Trigger: before each recursive planning iteration",
        "- Minimum interval: 30 minutes",
        "- Queries per cycle: up to 5",
        "",
        "## Project Priority Focus",
        "",
    ]
    if pulse["projectFocus"]:
        for item in pulse["projectFocus"]:
            lines.append(
                f"- {item['key']} ({item['priority']}, {item['status']}): {item['title']}"
            )
    else:
        lines.append("- No active TODO/IN_PROGRESS tasks detected.")

    lines.extend(["", "## Query Results", ""])
    for entry in pulse["queries"]:
        lines.append(f"### Query: {entry['query']}")
        lines.append(f"- Search URL: {entry['searchUrl']}")
        if not entry["results"]:
            lines.append("- No results parsed from Brave response.")
            lines.append("")
            continue
        for result in entry["results"]:
            lines.append(f"- {result['title']}")
            lines.append(f"  - URL: {result['url']}")
            lines.append(f"  - Domain: {result['domain']}")
            lines.append(f"  - Snippet: {result['snippet'][:180]}")
        lines.append("")
        lines.append(
            f"- Extracted keywords: {', '.join(entry['signals']['buzzwords'][:8])}"
        )
        lines.append("")

    lines.extend(
        [
            "## Top Signals",
            "",
            f"- Tools: {', '.join(pulse['topSignals']['tools']) or 'none'}",
            f"- Competitors: {', '.join(pulse['topSignals']['competitors'][:8]) or 'none'}",
            f"- Buzzwords: {', '.join(pulse['topSignals']['buzzwords'][:12]) or 'none'}",
            "",
            "## Planning Context Link",
            "",
            f"- Context JSON: `{pulse['contextPath']}`",
            f"- Proposal systems should reference this summary: `{pulse['summaryPath']}`",
        ]
    )
    return "\n".join(lines)


def run_pulse(args: argparse.Namespace) -> None:
    project_focus = parse_project_focus(args.project_path)
    queries = build_queries(project_focus, args.query or [])

    query_entries = []
    for query in queries:
        entry = search_brave(query, max_results=args.max_results)
        entry["capturedAt"] = utc_now()
        entry["signals"] = extract_keywords(entry["results"])
        query_entries.append(entry)

    pulse_id = datetime.now(timezone.utc).strftime("H013-%Y%m%dT%H%M%SZ")
    top_signals = aggregate_signals(query_entries)
    captured_at = utc_now()
    pulse = {
        "pulseId": pulse_id,
        "capturedAt": captured_at,
        "projectFocus": project_focus,
        "queries": query_entries,
        "topSignals": top_signals,
        "summaryPath": str(args.summary_path),
        "contextPath": str(args.context_path),
        "cadence": {
            "trigger": "before_each_recursive_planning_iteration",
            "minIntervalMinutes": args.min_interval_minutes,
            "maxQueriesPerCycle": len(queries),
        },
    }

    ensure_parent(args.summary_path)
    summary = render_summary_markdown(pulse)
    args.summary_path.write_text(summary, encoding="utf-8")

    ensure_parent(args.log_path)
    log = load_json_array(args.log_path)
    log.append(pulse)
    args.log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")

    context_payload = {
        "generatedAt": captured_at,
        "pulseId": pulse_id,
        "summaryPath": str(args.summary_path),
        "logPath": str(args.log_path),
        "priorityFocus": project_focus,
        "trendSignals": top_signals,
        "requiredForProposals": True,
        "guidance": (
            "Reference this pulse in proposal rationale so each recursive loop reflects "
            "current tools, competitors, and buzzwords."
        ),
    }
    ensure_parent(args.context_path)
    args.context_path.write_text(json.dumps(context_payload, indent=2), encoding="utf-8")

    print(f"Wrote Brave trend summary to {args.summary_path}")
    print(f"Appended pulse log to {args.log_path}")
    print(f"Wrote planning context to {args.context_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Brave trend pulse and store planning context artifacts for H013."
    )
    parser.add_argument(
        "--project-path",
        type=Path,
        default=PROJECT_PATH,
        help="Path to PROJECT.md for extracting active priorities.",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_SUMMARY_PATH,
        help="Output Markdown summary path.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Append-only JSON pulse log path.",
    )
    parser.add_argument(
        "--context-path",
        type=Path,
        default=DEFAULT_CONTEXT_PATH,
        help="Output planning context JSON path.",
    )
    parser.add_argument(
        "--query",
        action="append",
        help="Extra query to include in this pulse (can repeat).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum results to parse per query.",
    )
    parser.add_argument(
        "--min-interval-minutes",
        type=int,
        default=30,
        help="Documented minimum interval between trend pulses.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pulse(args)


if __name__ == "__main__":
    main()
