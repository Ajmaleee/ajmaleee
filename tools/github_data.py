from __future__ import annotations

import json
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "data_cache.json"
USER = "Ajmaleee"
UA = {"User-Agent": "Mozilla/5.0 (compatible; readme-stats)"}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    return re.sub(r"\s+", " ", value).strip()


def fetch_profile() -> dict:
    html = get(f"https://github.com/{USER}")
    followers = re.search(r'text-bold color-fg-default">([\d,]+)</span>\s*followers', html)
    following = re.search(r'text-bold color-fg-default">([\d,]+)</span>\s*following', html)
    name = re.search(r'<span class="p-name vcard-fullname[^"]*"[^>]*>([^<]*)</span>', html)
    bio = re.search(r'<div class="p-note user-profile-bio[^"]*"[^>]*>(.*?)</div>', html, re.S)
    return {
        "login": USER,
        "name": clean(name.group(1)) if name else USER,
        "bio": clean(bio.group(1)) if bio else "",
        "followers": int(followers.group(1).replace(",", "")) if followers else 0,
        "following": int(following.group(1).replace(",", "")) if following else 0,
    }


def parse_repos(html: str) -> list[dict]:
    parts = re.split(r'<li class="col-12[^"]*" itemprop="owns"', html)[1:]
    repos = []
    for block in parts:
        block = block.split("</li>", 1)[0]
        name = re.search(r'href="/[^/]+/([^"/]+)" itemprop="name codeRepository"', block)
        if not name:
            continue
        repo = name.group(1)
        desc = re.search(r'itemprop="description">(.*?)</p>', block, re.S)
        lang = re.search(r'itemprop="programmingLanguage">([^<]+)</span>', block)
        updated = re.search(r'<relative-time datetime="([^"]+)"', block)
        stars = re.search(rf'href="/[^/]+/{re.escape(repo)}/stargazers">(.*?)</a>', block, re.S)
        forks = re.search(rf'href="/[^/]+/{re.escape(repo)}/(?:forks|network/members)">(.*?)</a>', block, re.S)

        def count(match):
            if not match:
                return 0
            numbers = re.search(r"[\d,]+", clean(match.group(1)))
            return int(numbers.group(0).replace(",", "")) if numbers else 0

        repos.append({
            "name": repo,
            "description": clean(desc.group(1)) if desc else "",
            "language": clean(lang.group(1)) if lang else None,
            "stars": count(stars),
            "forks": count(forks),
            "updated": updated.group(1) if updated else None,
            "fork": bool(re.search(r'class="[^"]*\bfork\b', block)) or "Forked from" in block,
        })
    return repos


def fetch_repos() -> list[dict]:
    repos: list[dict] = []
    seen: set[str] = set()
    page = 1
    while page <= 10:
        html = get(f"https://github.com/{USER}?tab=repositories&page={page}")
        batch = parse_repos(html)
        fresh = [repo for repo in batch if repo["name"] not in seen]
        if not fresh:
            break
        for repo in fresh:
            seen.add(repo["name"])
            repos.append(repo)
        if len(batch) < 30:
            break
        page += 1
        time.sleep(0.4)
    return repos


def fetch_contributions() -> dict:
    html = get(f"https://github.com/users/{USER}/contributions")
    cells = re.findall(
        r'data-date="([0-9-]+)"[^>]*data-level="([0-4])"[^>]*>.*?<tool-tip[^>]*>([^<]*)</tool-tip>',
        html,
        re.S,
    )
    if not cells:
        cells = [
            (d, "0", tip)
            for d, tip in re.findall(
                r'data-date="([0-9-]+)"[^>]*>.*?<tool-tip[^>]*>([^<]*)</tool-tip>', html, re.S
            )
        ]
    days: dict[str, int] = {}
    levels: dict[str, int] = {}
    for day, level, tip in cells:
        match = re.match(r"(?:No|(\d[\d,]*)) contributions? on", tip)
        days[day] = 0 if tip.startswith("No") or not match or not match.group(1) else int(match.group(1).replace(",", ""))
        levels[day] = int(level)
    ordered = sorted(days)
    total = sum(days.values())
    active = sum(1 for value in days.values() if value > 0)
    best = current = 0
    best_end = None
    for day in ordered:
        if days[day] > 0:
            current += 1
            if current > best:
                best, best_end = current, day
        else:
            current = 0
    current = 0
    for day in reversed(ordered):
        if days[day] > 0:
            current += 1
        else:
            break
    return {
        "start": ordered[0] if ordered else None,
        "end": ordered[-1] if ordered else None,
        "days": days,
        "levels": levels,
        "total": total,
        "active_days": active,
        "longest_streak": best,
        "longest_end": best_end,
        "current_streak": current,
    }


def collect() -> dict:
    profile = fetch_profile()
    repos = fetch_repos()
    owned = [repo for repo in repos if not repo["fork"]]
    languages = Counter(repo["language"] for repo in owned if repo["language"])
    contributions = fetch_contributions()
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "profile": profile,
        "repos": repos,
        "owned_repos": len(owned),
        "public_repos": len(repos),
        "stars": sum(repo["stars"] for repo in repos),
        "forks": sum(repo["forks"] for repo in repos),
        "languages": languages.most_common(),
        "contributions": contributions,
    }


def main() -> None:
    data = collect()
    CACHE.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
    profile = data["profile"]
    print(f"user {profile['login']} repos {data['public_repos']} owned {data['owned_repos']} stars {data['stars']}")
    print(f"followers {profile['followers']} following {profile['following']}")
    print(f"contributions {data['contributions']['total']} active {data['contributions']['active_days']}")
    print("languages", data["languages"][:8])
    print(f"wrote {CACHE}")


if __name__ == "__main__":
    main()
