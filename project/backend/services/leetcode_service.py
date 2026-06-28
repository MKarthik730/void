"""
VOID — LeetCode Tracker
Track streak, stats, and suggest weak topics
"""

from typing import Optional, List
import requests
from datetime import datetime
import config

_leetcode_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 3600  # 1 hour


def get_stats(username: str = None) -> Optional[dict]:
    """Get LeetCode stats for a user."""
    if not username:
        username = config.LEETCODE_USERNAME

    global _leetcode_cache
    now = datetime.now().timestamp()
    if _leetcode_cache["data"] and (now - _leetcode_cache["timestamp"]) < CACHE_TTL:
        return _leetcode_cache["data"]

    try:
        # Using leetcode-stats-api (public)
        resp = requests.get(
            f"https://leetcode-stats-api.herokuapp.com/{username}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            stats = {
                "total_solved": data.get("totalSolved", 0),
                "easy": data.get("easySolved", 0),
                "medium": data.get("mediumSolved", 0),
                "hard": data.get("hardSolved", 0),
                "acceptance": data.get("acceptanceRate", 0),
                "ranking": data.get("ranking", 0),
                "streak": data.get("streak", 0),
                "contribution_points": data.get("contributionPoints", 0),
            }
            _leetcode_cache["data"] = stats
            _leetcode_cache["timestamp"] = now
            return stats
        return None
    except Exception:
        return None


def get_stats_formatted() -> str:
    """Get LeetCode stats formatted for daily brief."""
    stats = get_stats()
    if not stats:
        return "💪 LeetCode fetch avvaledhu"
    
    return (
        f"💪 **LeetCode** — {stats['total_solved']} total solved\n"
        f"  🟢 {stats['easy']} Easy | 🟡 {stats['medium']} Medium | 🔴 {stats['hard']} Hard\n"
        f"  📊 Acceptance: {stats['acceptance']}%"
    )
