"""Refresh profile statistics JSON and dark/light bento SVG cards from the GitHub REST API."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

THEMES = {
    "dark": {
        "card_bg": "#161b22",
        "border": "#30363d",
        "primary": "#f0f6fc",
        "secondary": "#8b949e",
        "muted": "#6e7681",
        "blue": "#58a6ff",
        "emerald": "#3fb950",
        "amber": "#e08256",
    },
    "light": {
        "card_bg": "#f6f8fa",
        "border": "#d0d7de",
        "primary": "#1f2328",
        "secondary": "#57606a",
        "muted": "#6e7681",
        "blue": "#0969da",
        "emerald": "#1a7f37",
        "amber": "#bc4c00",
    },
}

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def github_json(path: str) -> object:
    """Fetch a JSON payload from the GitHub REST API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jimmiy-profile-stats",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def collect_stats(username: str, api=github_json) -> dict:
    """Collect verified repository and upstream PR metrics for a GitHub user."""
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", username):
        raise ValueError("Invalid GitHub username")

    repos = []
    page = 1
    while True:
        batch = api(f"users/{username}/repos?per_page=100&type=owner&page={page}")
        repos.extend(
            r
            for r in batch
            if not r.get("private", False)
            and r.get("owner", {}).get("login", "").lower() == username.lower()
        )
        if len(batch) < 100:
            break
        page += 1

    original = [r for r in repos if not r.get("fork", False)]
    forks = [r for r in repos if r.get("fork", False)]

    result = {
        "username": username,
        "public_repos": len(repos),
        "original_repos": len(original),
        "fork_repos": len(forks),
        "total_stars": sum(int(r.get("stargazers_count", 0)) for r in repos),
        "original_stars": sum(int(r.get("stargazers_count", 0)) for r in original),
    }

    pr_queries = [
        ("upstream_merged_prs", f"type:pr author:{username} is:merged -user:{username}"),
        ("upstream_open_prs", f"type:pr author:{username} is:open -user:{username}"),
    ]
    for key, q in pr_queries:
        query = urllib.parse.urlencode({"q": q, "per_page": 1})
        found = api("search/issues?" + query)
        if found.get("incomplete_results"):
            raise RuntimeError(f"GitHub search returned incomplete results for {key}")
        result[key] = int(found["total_count"])

    result["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    result["source"] = "GitHub REST API; public owned repositories; upstream PRs across GitHub"
    return result


def render_stats_svg(stats: dict, theme: str = "dark") -> str:
    """Render a 4-column Precision Systems bento SVG card from collected stats."""
    if theme not in THEMES:
        raise ValueError(f"Unsupported theme: {theme}")

    c = THEMES[theme]
    updated_date = str(stats["updated_utc"])[:10]

    cards = [
        {
            "label": "UPSTREAM MERGED",
            "value": str(stats["upstream_merged_prs"]),
            "caption": "gdown · scapy",
            "accent": c["emerald"],
        },
        {
            "label": "UPSTREAM OPEN",
            "value": str(stats["upstream_open_prs"]),
            "caption": "j178/prek (Rust)",
            "accent": c["amber"],
        },
        {
            "label": "PUBLIC REPOS",
            "value": str(stats["public_repos"]),
            "caption": f"{stats['original_repos']} original · {stats['fork_repos']} forks",
            "accent": c["blue"],
        },
        {
            "label": "TOTAL STARS",
            "value": str(stats["total_stars"]),
            "caption": f"synced {updated_date}",
            "accent": c["primary"],
        },
    ]

    card_width = 214
    card_height = 104
    gap = 14
    start_x = 1
    card_y = 6

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="116" '
            f'viewBox="0 0 900 116" role="img" aria-labelledby="stats-title-{theme}">'
        ),
        f'  <title id="stats-title-{theme}">GitHub Stats Snapshot ({theme})</title>',
    ]

    for idx, item in enumerate(cards):
        x = start_x + idx * (card_width + gap)
        tx = x + 18
        label = html.escape(item["label"])
        value = html.escape(item["value"])
        caption = html.escape(item["caption"])
        accent = item["accent"]

        parts.extend(
            [
                f'  <g>',
                (
                    f'    <rect x="{x}" y="{card_y}" width="{card_width}" '
                    f'height="{card_height}" rx="10" fill="{c["card_bg"]}" stroke="{c["border"]}" />'
                ),
                f'    <circle cx="{tx + 4}" cy="{card_y + 22}" r="3.5" fill="{accent}" />',
                (
                    f'    <text x="{tx + 14}" y="{card_y + 26}" fill="{c["secondary"]}" '
                    f'font-family="{FONT_MONO}" font-size="10.5" font-weight="600" '
                    f'letter-spacing="1.1">{label}</text>'
                ),
                (
                    f'    <text x="{tx}" y="{card_y + 64}" fill="{c["primary"]}" '
                    f'font-family="{FONT_SANS}" font-size="28" font-weight="700">{value}</text>'
                ),
                (
                    f'    <text x="{tx}" y="{card_y + 88}" fill="{c["muted"]}" '
                    f'font-family="{FONT_MONO}" font-size="11">{caption}</text>'
                ),
                f'  </g>',
            ]
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--username",
        default=os.environ.get("GITHUB_REPOSITORY_OWNER", "jimi18102010-commits"),
    )
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    parser.add_argument("--json-out", type=Path, default=Path("profile-stats.json"))
    args = parser.parse_args()

    stats = collect_stats(args.username)
    dark_svg = render_stats_svg(stats, theme="dark")
    light_svg = render_stats_svg(stats, theme="light")

    args.assets_dir.mkdir(parents=True, exist_ok=True)
    (args.assets_dir / "stats-dark.svg").write_text(dark_svg, encoding="utf-8")
    (args.assets_dir / "stats-light.svg").write_text(light_svg, encoding="utf-8")
    args.json_out.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(f"Updated stats-dark.svg, stats-light.svg, and {args.json_out} from GitHub REST API.")


if __name__ == "__main__":
    main()
