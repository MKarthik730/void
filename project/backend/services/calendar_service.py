"""
VOID — Calendar Service
Google Calendar integration for schedule management
"""

import os
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict
import config

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def _get_service():
    """Get authenticated Calendar API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    token_path = config.GOOGLE_TOKEN_PATH
    secret_path = config.GOOGLE_CLIENT_SECRET_PATH

    # Try Gmail token first (shared SCOPES)
    gmail_token_path = token_path
    if os.path.exists(gmail_token_path):
        creds = Credentials.from_authorized_user_file(gmail_token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secret_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {secret_path}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_today_schedule() -> str:
    """Get today's calendar events."""
    try:
        service = _get_service()
    except FileNotFoundError as e:
        return f"📅 credentials.json ledhu bro — {str(e)}"
    except Exception as e:
        return f"📅 Calendar auth failed: {str(e)[:100]}"

    try:
        now = datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "📅 Ee roju events emi levu bro — free day!"

        lines = [f"📅 **Today's Schedule** ({len(events)} events)"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            title = event.get("summary", "No title")

            # Format time
            try:
                start_time = datetime.fromisoformat(start).strftime("%I:%M %p")
                end_time = datetime.fromisoformat(end).strftime("%I:%M %p")
                lines.append(f"  🕐 {start_time} - {end_time}")
            except (ValueError, TypeError):
                lines.append(f"  📌 All day")
            lines.append(f"     {title}")

        return "\n".join(lines)

    except Exception as e:
        return f"📅 Calendar fetch failed: {str(e)[:100]}"


def get_week_overview() -> str:
    """Get overview of the current week."""
    try:
        service = _get_service()
    except Exception as e:
        return f"📅 Calendar failed: {str(e)[:100]}"

    try:
        now = datetime.utcnow()
        week_end = now + timedelta(days=7)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=week_end.isoformat() + "Z",
                maxResults=30,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "📅 Ee week lo events emi levu bro"

        # Group by day
        from collections import defaultdict
        by_day = defaultdict(list)

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            title = event.get("summary", "No title")

            try:
                dt = datetime.fromisoformat(start)
                day_key = dt.strftime("%A, %b %d")
                time_str = dt.strftime("%I:%M %p") if "dateTime" in event["start"] else "All day"
                by_day[day_key].append(f"    🕐 {time_str} — {title}")
            except (ValueError, TypeError):
                by_day["Unknown"].append(f"    {title}")

        lines = [f"📅 **Week Overview** ({len(events)} events)"]
        for day, items in sorted(by_day.items()):
            lines.append(f"  **{day}**")
            lines.extend(items)

        return "\n".join(lines)

    except Exception as e:
        return f"📅 Week fetch failed: {str(e)[:100]}"


def add_event(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """Add an event to Google Calendar.

    Args:
        summary: Event title
        start_time: ISO format datetime string
        end_time: ISO format datetime string
        description: Optional description
    """
    try:
        service = _get_service()

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Kolkata",
            },
        }

        event = (
            service.events()
            .insert(calendarId="primary", body=event)
            .execute()
        )
        return f"✅ Event added: {summary} — {start_time[:16]} to {end_time[:16]}"

    except Exception as e:
        return f"❌ Event add cheyyadam lo error: {str(e)[:100]}"


def detect_conflicts() -> List[str]:
    """Detect overlapping events today."""
    try:
        service = _get_service()
    except Exception:
        return []

    try:
        now = datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        conflicts = []
        for i, e1 in enumerate(events):
            for e2 in events[i + 1:]:
                try:
                    s1 = e1["start"].get("dateTime", e1["start"].get("date"))
                    e1_end = e1["end"].get("dateTime", e1["end"].get("date"))
                    s2 = e2["start"].get("dateTime", e2["start"].get("date"))

                    dt1_start = datetime.fromisoformat(s1)
                    dt1_end = datetime.fromisoformat(e1_end)
                    dt2_start = datetime.fromisoformat(s2)
                    dt2_end = datetime.fromisoformat(
                        e2["end"].get("dateTime", e2["end"].get("date"))
                    )

                    if dt1_start < dt2_end and dt2_start < dt1_end:
                        conflicts.append(
                            f"  ⚠️ '{e1['summary']}' overlaps with '{e2['summary']}' "
                            f"at {dt2_start.strftime('%I:%M %p')}"
                        )
                except (ValueError, TypeError, KeyError):
                    continue

        return conflicts

    except Exception:
        return []


def suggest_focus_blocks() -> str:
    """Suggest free time blocks between events today for focused work."""
    try:
        service = _get_service()
    except Exception:
        return ""

    try:
        now = datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "🎯 Ee roju whole day free ga undi — build something! 🚀"

        # Find gaps between events
        gaps = []
        current = now
        for event in events:
            try:
                start = datetime.fromisoformat(
                    event["start"].get("dateTime", event["start"].get("date"))
                )
                if start > current:
                    gap_minutes = (start - current).seconds // 60
                    if gap_minutes >= 30:  # Only suggest 30+ min gaps
                        gaps.append(
                            f"  🕐 {current.strftime('%I:%M %p')} to {start.strftime('%I:%M %p')} "
                            f"({gap_minutes} min free)"
                        )
                end = datetime.fromisoformat(
                    event["end"].get("dateTime", event["end"].get("date"))
                )
                if end > current:
                    current = end
            except (ValueError, TypeError):
                continue

        # Check after last event
        if current < end_of_day:
            remaining = (end_of_day - current).seconds // 60
            if remaining >= 30:
                gaps.append(
                    f"  🕐 {current.strftime('%I:%M %p')} onwards ({remaining} min free)"
                )

        if gaps:
            return "🎯 **Focus Blocks Today**\n" + "\n".join(gaps[:3])
        return ""

    except Exception:
        return ""
