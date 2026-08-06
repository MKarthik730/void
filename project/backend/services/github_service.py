"""
VOID — GitHub Service
Track public repos, commits, PRs, stars for MKarthik730
"""

import requests
from typing import List, Optional
from datetime import datetime
import config

_github_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 600  # 10 minutes


def _get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
    return headers


def get_recent_activity(username: str = None) -> List[str]:
    """Get recent GitHub activity: events, PRs, repos."""
    if not username:
        username = config.GITHUB_USERNAME

    global _github_cache
    now = datetime.now().timestamp()
    if _github_cache["data"] and (now - _github_cache["timestamp"]) < CACHE_TTL:
        return _github_cache["data"]

    lines = []

    # Get user repos
    try:
        resp = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=_get_headers(),
            params={"sort": "updated", "per_page": 10},
            timeout=10,
        )
        if resp.status_code == 200:
            repos = resp.json()
            if repos:
                lines.append(f"/{username} — {len(repos)} public repos")
        elif resp.status_code == 403:
            lines.append("GitHub API rate limit hit — try later")
    except Exception:
        lines.append("GitHub fetch failed")

    # Get recent events (pushes, PRs)
    try:
        resp = requests.get(
            f"https://api.github.com/users/{username}/events/public",
            headers=_get_headers(),
            params={"per_page": 5},
            timeout=10,
        )
        if resp.status_code == 200:
            for event in resp.json()[:5]:
                repo = event["repo"]["name"].split("/")[1]
                etype = event["type"]
                if etype == "PushEvent":
                    commits = len(event["payload"].get("commits", []))
                    lines.append(f"  Committed {commits}x to {repo}")
                elif etype == "CreateEvent":
                    ref = event["payload"].get("ref", "branch")
                    lines.append(f"  Created {ref} in {repo}")
                elif etype == "IssuesEvent":
                    action = event["payload"].get("action", "")
                    lines.append(f"  {action.capitalize()} issue in {repo}")
                elif etype == "WatchEvent":
                    lines.append(f"  Starred a repo")
    except Exception:
        pass

    # Get pull requests authored by user
    try:
        resp = requests.get(
            "https://api.github.com/search/issues",
            headers=_get_headers(),
            params={
                "q": f"author:{username} type:pr is:open",
                "per_page": 5,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            open_prs = resp.json().get("total_count", 0)
            if open_prs > 0:
                lines.append(f"  {open_prs} open PRs")
    except Exception:
        pass

    # Check known repos for new stars
    known_repos = ["Memoir", "Cognitus", "DevCollab", "VOID", "Aegis", "AI-Resume-Ranker"]
    for repo_name in known_repos:
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{username}/{repo_name}",
                headers=_get_headers(),
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                stars = data.get("stargazers_count", 0)
                if stars > 0:
                    lines.append(f"  {repo_name}: ⭐ {stars} stars")
        except Exception:
            continue

    if not lines:
        lines = ["No GitHub activity fetched"]

    _github_cache["data"] = lines
    _github_cache["timestamp"] = now
    return lines


def get_repo_status(repo_name: str) -> Optional[str]:
    """Get status of a specific repo."""
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{config.GITHUB_USERNAME}/{repo_name}",
            headers=_get_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return (
                f"{repo_name}: {data.get('description', 'No description')}\n"
                f"  ⭐ {data['stargazers_count']} | 🍴 {data['forks_count']} | "
                f"⚠️ {data['open_issues_count']} issues\n"
                f"  Last push: {data['pushed_at'][:10]}"
            )
        return None
    except Exception:
        return None


def get_github_overview() -> str:
    """Formatted overview for daily brief."""
    activity = get_recent_activity()
    if not activity or "No GitHub" in activity[0]:
        return "💻 GitHub fetch avvaledhu"
    return "💻 **GitHub**\n" + "\n".join(activity)
