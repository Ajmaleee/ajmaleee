from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "data_cache.json"
OUT = ROOT / "assets" / "generated"
W = 560
H = 504
PAD = 20
PITCH = 9
CELL = 7
GRID_X = 54
GRID_Y = 398

THEMES = {
    "dark": {
        "bg": "#070b08",
        "card": "#0a100c",
        "border": "#1b2c20",
        "text": "#cdded2",
        "muted": "#6d8a75",
        "accent": "#7cf2a4",
        "bright": "#b8ffcf",
        "track": "#142218",
        "levels": ["#101a13", "#1c4429", "#2d7a43", "#49b96a", "#8df0a4"],
    },
    "light": {
        "bg": "#f6f9f6",
        "card": "#ffffff",
        "border": "#ccdcd0",
        "text": "#1c2c21",
        "muted": "#617c68",
        "accent": "#1c7a42",
        "bright": "#0f5a2f",
        "track": "#e2ece5",
        "levels": ["#e6eee8", "#c2e4cb", "#84c997", "#3f9d5d", "#146b36"],
    },
}


def mark(x: int, baseline: int, text: str, theme: dict, *, size: float, fill: str, anchor: str = "start",
         weight: int = 400, spacing: float = 0.0, opacity: float = 1.0) -> str:
    return (
        f'<text x="{x}" y="{baseline}" fill="{theme[fill]}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}" '
        f'opacity="{opacity}">{escape(text)}</text>'
    )


def leader(x1: int, x2: int, y: int, theme: dict) -> str:
    return (
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{theme["muted"]}" '
        f'stroke-width="1" stroke-dasharray="2 3" opacity="0.75"/>'
    )


def render(data: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    profile = data["profile"]
    contributions = data["contributions"]
    languages = data["languages"]
    parts: list[str] = []
    add = parts.append

    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">'
    )
    add("<title id=\"title\">GitHub system monitor for Ajmaleee</title>")
    add(
        "<desc id=\"desc\">Repository, language, contribution and streak statistics "
        "generated from the public GitHub profile.</desc>"
    )
    add(f'<rect width="{W}" height="{H}" fill="{theme["bg"]}"/>')
    add(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="7" '
        f'fill="{theme["card"]}" stroke="{theme["border"]}"/>'
    )
    add(f'<rect x="0" y="0" width="{W}" height="2" fill="{theme["accent"]}" opacity="0.85"/>')
    add(
        f'<g font-family="ui-monospace, SFMono-Regular, \'SF Mono\', Menlo, Consolas, '
        f'\'Liberation Mono\', monospace">'
    )

    add(mark(PAD, 23, "SYSTEM MONITOR", theme, size=11, fill="accent", weight=700, spacing=2.0))
    add(mark(W - PAD, 23, "@AJMALEE", theme, size=9.5, fill="muted", anchor="end", spacing=1.4))
    add(f'<line x1="{PAD}" y1="34" x2="{W - PAD}" y2="34" stroke="{theme["border"]}"/>')

    add(mark(PAD, 58, "01 / IDENTITY", theme, size=11.5, fill="accent", weight=600, spacing=2.0))
    stats = [
        ("PUBLIC REPOS", str(data["public_repos"]), "TOTAL STARS", str(data["stars"])),
        ("FOLLOWERS", str(profile["followers"]), "FOLLOWING", str(profile["following"])),
        ("CONTRIBUTIONS", str(contributions["total"]), "ACTIVE DAYS", str(contributions["active_days"])),
        ("LONGEST STREAK", f'{contributions["longest_streak"]}d', "CURRENT STREAK", f'{contributions["current_streak"]}d'),
    ]
    y = 86
    for left_label, left_value, right_label, right_value in stats:
        add(mark(PAD, y, left_label, theme, size=10.5, fill="muted", spacing=1.4))
        add(leader(150, 214, y - 3, theme))
        add(mark(250, y, left_value, theme, size=15, fill="bright", anchor="end", weight=700))
        add(mark(300, y, right_label, theme, size=10.5, fill="muted", spacing=1.4))
        add(leader(438, 510, y - 3, theme))
        add(mark(W - PAD, y, right_value, theme, size=15, fill="bright", anchor="end", weight=700))
        y += 24

    add(f'<line x1="{PAD}" y1="174" x2="{W - PAD}" y2="174" stroke="{theme["border"]}"/>')
    add(mark(PAD, 198, "02 / LANGUAGE MIX", theme, size=11.5, fill="accent", weight=600, spacing=2.0))
    with_language = sum(count for _, count in languages)
    add(mark(W - PAD, 198, f"{with_language} REPOS / PRIMARY", theme, size=9, fill="muted", anchor="end", spacing=0.8))

    top = languages[:5]
    other = sum(count for _, count in languages[5:])
    rows = list(top) + ([("OTHER", other)] if other else [])
    maximum = max(count for _, count in rows)
    bar_x, bar_w = 148, 362
    y = 220
    for name, count in rows:
        add(mark(PAD, y, name.upper(), theme, size=11, fill="text", spacing=1.2))
        add(mark(136, y, str(count), theme, size=11, fill="muted", anchor="end"))
        add(f'<rect x="{bar_x}" y="{y - 9}" width="{bar_w}" height="6" rx="1.5" fill="{theme["track"]}"/>')
        width = max(3, round(bar_w * count / maximum))
        add(f'<rect x="{bar_x}" y="{y - 9}" width="{width}" height="6" rx="1.5" fill="{theme["accent"]}" opacity="0.9"/>')
        y += 21

    add(f'<line x1="{PAD}" y1="344" x2="{W - PAD}" y2="344" stroke="{theme["border"]}"/>')
    add(mark(PAD, 368, "03 / ACTIVITY", theme, size=11.5, fill="accent", weight=600, spacing=2.0))
    add(
        mark(
            W - PAD, 368, f'{contributions["total"]} CONTRIBUTIONS / LAST 12 MONTHS', theme,
            size=9, fill="muted", anchor="end", spacing=0.8,
        )
    )

    days = contributions["days"]
    levels = contributions["levels"]
    first = date.fromisoformat(contributions["start"])
    month_seen: set[tuple[int, int]] = set()
    month_labels: list[tuple[int, str]] = []
    for iso in sorted(days):
        current = date.fromisoformat(iso)
        week = (current - first).days // 7
        dow = (current.weekday() + 1) % 7
        level = levels.get(iso, 0)
        add(
            f'<rect x="{GRID_X + week * PITCH}" y="{GRID_Y + dow * PITCH}" width="{CELL}" '
            f'height="{CELL}" rx="1.2" fill="{theme["levels"][level]}"/>'
        )
        if (current.year, current.month) not in month_seen:
            month_seen.add((current.year, current.month))
            month_labels.append((week, current.strftime("%b").upper()))

    for week, label in month_labels:
        x = GRID_X + week * PITCH
        if x + 16 <= W - PAD:
            add(mark(x, 388, label, theme, size=8, fill="muted", spacing=0.8))
    for dow, label in ((1, "MON"), (3, "WED"), (5, "FRI")):
        add(mark(GRID_X - 8, GRID_Y + dow * PITCH + 6, label, theme, size=8, fill="muted", anchor="end", spacing=0.5))

    add(mark(GRID_X, 476, "LESS", theme, size=8, fill="muted", spacing=0.8))
    lx = GRID_X + 30
    for level in range(5):
        add(f'<rect x="{lx}" y="469" width="{CELL}" height="{CELL}" rx="1.2" fill="{theme["levels"][level]}"/>')
        lx += 11
    add(mark(lx + 2, 476, "MORE", theme, size=8, fill="muted", spacing=0.8))

    add(f'<line x1="{PAD}" y1="484" x2="{W - PAD}" y2="484" stroke="{theme["border"]}"/>')
    synced = data["generated_at"].replace("T", " ").replace("Z", "Z")
    add(mark(PAD, 497, f"LAST SYNC {synced}", theme, size=8.5, fill="muted", spacing=0.6))
    add(mark(W - PAD, 497, "SOURCE GITHUB / AJMALEE", theme, size=8.5, fill="muted", anchor="end", spacing=0.6))
    add("</g></svg>")
    return "".join(parts)


def main() -> None:
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    if not data.get("generated_at"):
        data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("dark", "light"):
        path = OUT / f"system-{name}.svg"
        path.write_text(render(data, name), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
