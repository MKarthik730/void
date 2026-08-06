"""
VOID — Scheduler
Daily digest, morning brief, periodic tasks
Runs in background thread alongside the FastAPI server
"""

import threading
import time
import os
from datetime import datetime
import config


def _get_current_time_ist():
    """Get current time in IST (UTC+5:30)."""
    import pytz
    try:
        ist = pytz.timezone("Asia/Kolkata")
        return datetime.now(ist)
    except ImportError:
        # Fallback without pytz
        from datetime import timezone, timedelta
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(ist_offset)


# ── Daily Brief (Morning) ─────────────────────────────────────────────────────
def generate_morning_brief() -> str:
    """Generate the morning brief with all components."""
    from services.weather_service import get_weather_short
    from services.news_service import get_tech_news_formatted
    from services.github_service import get_github_overview
    from services.leetcode_service import get_stats_formatted
    from services.memory_service import get_context_for_query

    # Weather
    weather = get_weather_short()

    # Schedule
    try:
        from services.calendar_service import get_today_schedule
        schedule = get_today_schedule()
    except Exception:
        schedule = "📅 Calendar setup avvaledhu"

    # Email summary
    try:
        from services.gmail_service import check_inbox
        emails = check_inbox(5)
        if emails and "error" not in emails[0]:
            urgent = [e for e in emails if e.get("category") == "🔴 Urgent"]
            email_summary = (
                f"📧 {len(urgent)} urgent emails"
                if urgent
                else f"📧 {len(emails)} unread"
            )
        else:
            email_summary = "📧 Email fetch avvaledhu"
    except Exception:
        email_summary = "📧 Email setup avvaledhu"

    # GitHub
    github = get_github_overview()

    # Tech news
    news = get_tech_news_formatted(3)

    # LeetCode
    leetcode = get_stats_formatted()

    # Daily priority
    from services.focus_service import suggest_pomodoro
    priority = suggest_pomodoro()

    # Dev tip rotation
    dev_tips = [
        "💡 **Tip:** Use 'git stash' to temporarily save uncommitted changes",
        "💡 **Tip:** Use pgvector's <=> operator for cosine similarity in RAG",
        "💡 **Tip:** LangGraph's StateGraph is perfect for multi-step agent workflows",
        "💡 **Tip:** Use UV for Python package management — it's 10x faster than pip",
        "💡 **Tip:** FastAPI's background tasks are great for non-blocking operations",
        "💡 **Tip:** Use React Query for server state management in your frontends",
        "💡 **Tip:** Redis Streams > Redis Pub/Sub for reliable message queues",
        "💡 **Tip:** Use 'pre-commit' hooks to catch secrets before they hit GitHub",
    ]
    # Pick tip based on day of month
    import datetime as dt
    tip_index = dt.date.today().day % len(dev_tips)
    tip = dev_tips[tip_index]

    brief = (
        f"☀️ **GOOD MORNING BRO!** ☀️\n\n"
        f"{weather}\n\n"
        f"{schedule}\n\n"
        f"{email_summary}\n\n"
        f"{github}\n\n"
        f"{news}\n\n"
        f"{leetcode}\n\n"
        f"🎯 **Today's Priority:** {priority}\n\n"
        f"{tip}\n\n"
        f"_Daily brief generated at {datetime.now().strftime('%I:%M %p')}_"
    )

    return brief


# ── Daily Digest (Evening) ────────────────────────────────────────────────────
def generate_daily_digest() -> str:
    """Generate the end-of-day daily digest."""
    from services.memory_service import get_context_for_query
    from services.github_service import get_recent_activity
    from services.leetcode_service import get_stats
    from services.weather_service import get_weather_short

    # What was built (from git)
    from services.git_service import get_diff
    diff = get_diff()
    has_changes = len(diff) > 10 if diff else False

    # GitHub activity
    github = get_recent_activity()
    github_line = github[0] if github else "No activity"

    # LeetCode
    leetcode_stats = get_stats()
    leetcode_line = (
        f"Solved: {leetcode_stats['total_solved']} total"
        if leetcode_stats else "No stats"
    )

    # Tomorrow's weather
    tomorrow_weather = get_weather_short()

    # Get today's events from calendar
    try:
        from services.calendar_service import get_today_schedule
        today_schedule = get_today_schedule()
    except Exception:
        today_schedule = ""

    # Gather sessions from memory
    sessions = get_context_for_query("Session completed", memory_limit=3, history_limit=0)

    digest = (
        f"🌙 **DAILY DIGEST** 🌙\n"
        f"{datetime.now().strftime('%A, %b %d, %Y')}\n\n"
        f"**What was built today:**\n"
        f"{'  ✅ Code changes detected' if has_changes else '  ❌ No code changes'}\n"
        f"  {github_line}\n\n"
        f"**LeetCode:** {leetcode_line}\n\n"
        f"**Today's Schedule:**\n"
        f"{today_schedule if today_schedule else '  No events tracked'}\n\n"
        f"**Sessions:**\n"
        f"{sessions if sessions else '  No sessions tracked'}\n\n"
        f"**Tomorrow Weather:** {tomorrow_weather}\n\n"
        f"**Prep for tomorrow:**\n"
        f"  1. Review what's pending\n"
        f"  2. Plan 3 things to accomplish\n"
        f"  3. Sleep well bro — 7-8 hours! 😴\n\n"
        f"_Good night bro! 🚀_"
    )

    return digest


# ── Scheduler Engine ──────────────────────────────────────────────────────────
_scheduler_running = False


def _morning_brief_job():
    """Deliver morning brief at 8 AM IST."""
    brief = generate_morning_brief()
    # In production, this would send a notification or email
    print(f"\n{'='*50}")
    print(f"[VOID SCHEDULER] Morning Brief — {datetime.now()}")
    print(f"{'='*50}")
    print(brief)
    print(f"{'='*50}\n")

    # Store in memory
    from services.memory_service import add_memory
    add_memory(
        f"Morning brief delivered: {datetime.now().strftime('%b %d')}",
        category="productivity",
        importance=2,
    )


def _daily_digest_job():
    """Deliver daily digest at 10 PM IST."""
    digest = generate_daily_digest()
    print(f"\n{'='*50}")
    print(f"[VOID SCHEDULER] Daily Digest — {datetime.now()}")
    print(f"{'='*50}")
    print(digest)
    print(f"{'='*50}\n")

    # Store in memory
    from services.memory_service import add_memory
    add_memory(
        f"Daily digest delivered: {datetime.now().strftime('%b %d')}",
        category="productivity",
        importance=2,
    )


def _leetcode_streak_check():
    """Check LeetCode streak at 9 PM IST."""
    from services.leetcode_service import get_stats
    stats = get_stats()
    if stats:
        streak = stats.get("streak", 0)
        if streak == 0:
            print(f"\n[VOID SCHEDULER] LeetCode streak broken bro! Easy problem cheyyi!")
        elif streak < 7:
            print(f"\n[VOID SCHEDULER] LeetCode: {streak}-day streak — keep going bro!")
        else:
            print(f"\n[VOID SCHEDULER] LeetCode: 🔥 {streak}-day streak! Consistent bro!")

    # Schedule next
    _schedule_daily("21:00", _leetcode_streak_check)


def _schedule_daily(time_str: str, job_func):
    """Schedule a job to run daily at a specific time.

    Args:
        time_str: HH:MM format (IST)
        job_func: Function to call
    """
    try:
        import schedule as sched_lib
        # Convert IST to schedule-compatible time
        sched_lib.every().day.at(time_str).do(job_func)
    except ImportError:
        # Manual scheduling fallback
        def _run_check():
            while _scheduler_running:
                now = _get_current_time_ist()
                if now.strftime("%H:%M") == time_str:
                    job_func()
                    time.sleep(61)  # Avoid re-trigger
                time.sleep(30)
        threading.Thread(target=_run_check, daemon=True).start()


def start_scheduler():
    """Start the background scheduler."""
    global _scheduler_running
    if _scheduler_running:
        return

    _scheduler_running = True
    print("[VOID SCHEDULER] Starting scheduler...")

    try:
        import schedule as sched_lib

        # Scheduler uses system local time. If system is in IST, use IST times directly.
        # Morning brief: 8 AM IST
        sched_lib.every().day.at("08:00").do(_morning_brief_job)

        # LeetCode streak check: 9 PM IST
        sched_lib.every().day.at("21:00").do(_leetcode_streak_check)

        # Daily digest: 10 PM IST
        sched_lib.every().day.at("22:00").do(_daily_digest_job)

        def _run():
            while _scheduler_running:
                sched_lib.run_pending()
                time.sleep(60)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        print("[VOID SCHEDULER] Scheduler running (brief: 8AM, digest: 10PM IST)")

    except ImportError:
        print("[VOID SCHEDULER] 'schedule' package not found — using fallback")
        # Manual check every 30 seconds
        _schedule_daily("08:00", _morning_brief_job)  # 8 AM IST
        _schedule_daily("21:00", _leetcode_streak_check)  # 9 PM IST
        _schedule_daily("22:00", _daily_digest_job)  # 10 PM IST


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler_running
    _scheduler_running = False
    print("[VOID SCHEDULER] Stopped")
