"""Refresh the single activity card using GitHub's contribution calendar."""
import datetime
import json
import os
from pathlib import Path
import urllib.request


def render(total: int, date: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="96" viewBox="0 0 960 96" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity</title>
<desc id="desc">{total} contributions in the past year. Updated {date}.</desc>
<rect width="960" height="96" rx="4" fill="#0d1117"/>
<path d="M0 .5H960" stroke="#30363d"/>
<text x="18" y="60" font-family="Consolas,monospace" font-size="36" fill="#9dcab2">{total}</text>
<text x="120" y="58" font-family="Arial,Helvetica,sans-serif" font-size="18" fill="#9ba7b4">GitHub contributions in the past year</text>
<text x="940" y="58" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#9ba7b4">Updated {date}</text>
</svg>'''


def main() -> None:
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "BhavyaP45")
    query = "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions}}}}"
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": owner}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Content-Type": "application/json", "User-Agent": "forest-profile"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("errors"):
        raise RuntimeError("GitHub contribution query failed: " + json.dumps(result["errors"]))
    total = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    if not isinstance(total, int) or total < 0:
        raise ValueError("Invalid contribution count")
    date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    output = Path(__file__).resolve().parents[1] / "assets" / "activity.svg"
    output.write_text(render(total, date), encoding="utf-8")


if __name__ == "__main__":
    main()
