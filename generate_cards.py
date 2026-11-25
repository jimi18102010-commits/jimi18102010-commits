"""Refresh profile statistics JSON and dark/light hero & bento SVG cards from the GitHub REST API."""
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

BIRTH_DATE = dt.date(2010, 10, 18)
UZBEKISTAN_TZ = dt.timezone(dt.timedelta(hours=5))

THEMES = {
    "dark": {
        "canvas": "#0d1117",
        "card_bg": "#161b22",
        "border": "#30363d",
        "grid": "#21262d",
        "primary": "#f0f6fc",
        "secondary": "#8b949e",
        "muted": "#6e7681",
        "blue": "#58a6ff",
        "emerald": "#3fb950",
        "amber": "#e08256",
        "pill_stroke_opacity": "0.55",
        "dot_opacity": "0.6",
    },
    "light": {
        "canvas": "#ffffff",
        "card_bg": "#f6f8fa",
        "border": "#d0d7de",
        "grid": "#eaeef2",
        "primary": "#1f2328",
        "secondary": "#57606a",
        "muted": "#6e7681",
        "blue": "#0969da",
        "emerald": "#1a7f37",
        "amber": "#bc4c00",
        "pill_stroke_opacity": "0.45",
        "dot_opacity": "0.55",
    },
}

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def compute_age(birth_date: dt.date = BIRTH_DATE, today: dt.date | None = None) -> int:
    """Compute current age in Uzbekistan time (UTC+5) from the given birth date."""
    if today is None:
        today = dt.datetime.now(UZBEKISTAN_TZ).date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def github_json(path: str) -> object:
    """Fetch a JSON payload from the GitHub REST API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jimmy-profile-stats",
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


def render_hero_svg(age: int, theme: str = "dark") -> str:
    """Render the dark/light Precision Systems hero SVG with the current developer age."""
    if theme not in THEMES:
        raise ValueError(f"Unsupported theme: {theme}")

    c = THEMES[theme]
    age_text = html.escape(f"{age} y.o.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220" viewBox="0 0 900 220" role="img" aria-labelledby="hero-{theme}-title hero-{theme}-desc">
  <title id="hero-{theme}-title">Jimmy — Systems &amp; Low-Latency Developer</title>
  <desc id="hero-{theme}-desc">GitHub profile header for Jimmy, based in Uzbekistan, focused on Rust, C, eBPF/XDP, and Linux systems tooling.</desc>
  <defs>
    <pattern id="dot-grid-{theme}" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="{c['grid']}" />
    </pattern>
    <linearGradient id="accent-fade-{theme}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{c['blue']}" stop-opacity="0.22" />
      <stop offset="100%" stop-color="{c['blue']}" stop-opacity="0" />
    </linearGradient>
    <clipPath id="card-clip-{theme}">
      <rect x="0.5" y="0.5" width="899" height="219" rx="12" />
    </clipPath>
  </defs>

  <g clip-path="url(#card-clip-{theme})">
    <rect x="0" y="0" width="900" height="220" fill="{c['canvas']}" />
    <rect x="520" y="0" width="380" height="220" fill="url(#dot-grid-{theme})" />
    <rect x="0" y="0" width="900" height="2" fill="url(#accent-fade-{theme})" />
  </g>
  <rect x="0.5" y="0.5" width="899" height="219" rx="12" fill="none" stroke="{c['border']}" />

  <!-- Left column: Identity & Focus -->
  <g font-family="{FONT_SANS}">
    <rect x="28" y="34" width="4" height="20" rx="2" fill="{c['blue']}" />
    <text x="42" y="49" fill="{c['secondary']}" font-family="{FONT_MONO}" font-size="11.5" font-weight="600" letter-spacing="2">UZBEKISTAN  //  SYSTEMS &amp; LOW-LATENCY</text>

    <text x="28" y="100" fill="{c['primary']}" font-size="42" font-weight="700" letter-spacing="-0.5">Jimmy</text>
    <text x="28" y="131" fill="{c['secondary']}" font-size="14.5" font-weight="400">Linux kernel internals, eBPF/XDP, Rust tooling &amp; zero-bloat engineering.</text>

    <!-- Focus pills -->
    <g font-family="{FONT_MONO}" font-size="11.5" font-weight="600">
      <rect x="28" y="156" width="112" height="26" rx="6" fill="{c['card_bg']}" stroke="{c['amber']}" stroke-opacity="{c['pill_stroke_opacity']}" />
      <circle cx="43" cy="169" r="3.5" fill="{c['amber']}" />
      <text x="54" y="173" fill="{c['primary']}">Rust · egui</text>

      <rect x="150" y="156" width="136" height="26" rx="6" fill="{c['card_bg']}" stroke="{c['emerald']}" stroke-opacity="{c['pill_stroke_opacity']}" />
      <circle cx="165" cy="169" r="3.5" fill="{c['emerald']}" />
      <text x="176" y="173" fill="{c['primary']}">C · eBPF / XDP</text>

      <rect x="296" y="156" width="174" height="26" rx="6" fill="{c['card_bg']}" stroke="{c['blue']}" stroke-opacity="{c['pill_stroke_opacity']}" />
      <circle cx="311" cy="169" r="3.5" fill="{c['blue']}" />
      <text x="322" y="173" fill="{c['primary']}">Python · Systems CLI</text>
    </g>
  </g>

  <!-- Right column: Minimalist telemetry window -->
  <g>
    <rect x="600" y="32" width="272" height="156" rx="10" fill="{c['card_bg']}" stroke="{c['border']}" />
    <line x1="600" y1="62" x2="872" y2="62" stroke="{c['border']}" />
    <circle cx="618" cy="47" r="3.5" fill="{c['muted']}" opacity="{c['dot_opacity']}" />
    <circle cx="630" cy="47" r="3.5" fill="{c['muted']}" opacity="{c['dot_opacity']}" />
    <circle cx="642" cy="47" r="3.5" fill="{c['muted']}" opacity="{c['dot_opacity']}" />
    <text x="658" y="51" fill="{c['secondary']}" font-family="{FONT_MONO}" font-size="11.5">~/profile.env</text>

    <g font-family="{FONT_MONO}" font-size="12">
      <text x="618" y="88" fill="{c['muted']}">AGE</text>
      <text x="698" y="88" fill="{c['emerald']}" font-weight="600">{age_text}</text>

      <text x="618" y="113" fill="{c['muted']}">BASE</text>
      <text x="698" y="113" fill="{c['primary']}">Uzbekistan</text>

      <text x="618" y="138" fill="{c['muted']}">FOCUS</text>
      <text x="698" y="138" fill="{c['primary']}">Rust · C · Linux</text>

      <text x="618" y="163" fill="{c['muted']}">UPSTREAM</text>
      <text x="698" y="163" fill="{c['blue']}">gdown · scapy</text>
    </g>
  </g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--username",
        default=os.environ.get("GITHUB_REPOSITORY_OWNER", "jimi18102010-commits"),
    )
    parser.add_argument("--birth-date", default=BIRTH_DATE.isoformat())
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    parser.add_argument("--json-out", type=Path, default=Path("profile-stats.json"))
    args = parser.parse_args()

    birth_date = dt.date.fromisoformat(args.birth_date)
    age = compute_age(birth_date)
    stats = collect_stats(args.username)
    stats["age"] = age

    hero_dark_svg = render_hero_svg(age, theme="dark")
    hero_light_svg = render_hero_svg(age, theme="light")
    stats_dark_svg = render_stats_svg(stats, theme="dark")
    stats_light_svg = render_stats_svg(stats, theme="light")

    args.assets_dir.mkdir(parents=True, exist_ok=True)
    (args.assets_dir / "hero-dark.svg").write_text(hero_dark_svg, encoding="utf-8")
    (args.assets_dir / "hero-light.svg").write_text(hero_light_svg, encoding="utf-8")
    (args.assets_dir / "stats-dark.svg").write_text(stats_dark_svg, encoding="utf-8")
    (args.assets_dir / "stats-light.svg").write_text(stats_light_svg, encoding="utf-8")
    args.json_out.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(f"Updated hero & stats SVGs (age={age}) and {args.json_out} from GitHub REST API.")


if __name__ == "__main__":
    main()
