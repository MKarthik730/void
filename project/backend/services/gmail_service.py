"""
VOID — Gmail Service
Email intelligence: read, categorize, draft replies
"""

import os
import base64
import re
from email.message import EmailMessage
from typing import Optional, List, Dict
from datetime import datetime, timedelta

import config

# Google APIs
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def _get_service():
    """Get authenticated Gmail API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    token_path = config.GOOGLE_TOKEN_PATH
    secret_path = config.GOOGLE_CLIENT_SECRET_PATH

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

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
        # Save token
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _categorize_email(subject: str, snippet: str, from_email: str) -> str:
    """Categorize an email by priority."""
    subject_lower = (subject or "").lower()
    snippet_lower = (snippet or "").lower()
    from_lower = (from_email or "").lower()

    # Urgent keywords
    urgent_keywords = [
        "deadline", "urgent", "asap", "immediately", "due tomorrow",
        "interview", "otp", "verification code", "last date",
    ]
    if any(kw in subject_lower or kw in snippet_lower for kw in urgent_keywords):
        return "🔴 Urgent"

    # Internship / Recruiter
    internship_keywords = [
        "internship", "recruiter", "application", "hiring", "job offer",
        "opportunity", "role at", "we are hiring", "your application",
        "interview invitation", "offer letter",
    ]
    if any(kw in subject_lower or kw in snippet_lower for kw in internship_keywords):
        return "🟡 Internship"

    # Hackathon platforms
    hackathon_domains = [
        "hack2skill", "devnetwork", "devfolio", "hackerearth",
        "unstop", "dare2compete",
    ]
    if any(domain in from_lower for domain in hackathon_domains):
        return "🟠 Hackathon"

    # College / Academic
    college_keywords = [
        "anits", "college", "exam", "assignment", "class", "timetable",
        "academic", "faculty", "professor", "grade", "cgpa",
    ]
    if any(kw in subject_lower or kw in snippet_lower for kw in college_keywords):
        return "🔵 Academic"

    # Notification services
    notification_domains = [
        "github", "vercel", "render", "google", "gcp",
        "notifications@", "noreply@",
    ]
    if any(domain in from_lower for domain in notification_domains):
        return "⚪ Notification"

    # Newsletters
    newsletter_keywords = [
        "newsletter", "weekly digest", "this week in", "daily.dev",
        "medium daily",
    ]
    if any(kw in subject_lower for kw in newsletter_keywords):
        return "⬜ Newsletter"

    return "🔵 Other"


def check_inbox(max_results: int = 20) -> List[Dict]:
    """Get unread inbox emails grouped by priority."""
    try:
        service = _get_service()
    except FileNotFoundError as e:
        return [{"error": f"credentials.json ledhu bro — {str(e)}"}]
    except Exception as e:
        return [{"error": f"Gmail auth failed: {str(e)[:100]}"}]

    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", q="in:inbox", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])
        if not messages:
            return [{"category": "ℹ️", "subject": "Inbox lo emails emi levu bro"}]

        email_list = []
        for msg in messages[:max_results]:
            msg_data = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = ""
            sender = ""
            date = ""
            for h in headers:
                if h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "From":
                    sender = h["value"]
                elif h["name"] == "Date":
                    date = h["value"]

            snippet = msg_data.get("snippet", "")
            category = _categorize_email(subject, snippet, sender)
            is_unread = "UNREAD" in msg_data.get("labelIds", [])

            email_list.append({
                "id": msg["id"],
                "subject": subject,
                "from": sender,
                "snippet": snippet,
                "category": category,
                "unread": is_unread,
                "date": date,
            })

        # Sort by priority: Urgent first, then Internship, etc.
        priority_order = {
            "🔴 Urgent": 0,
            "🟡 Internship": 1,
            "🟠 Hackathon": 2,
            "🔵 Academic": 3,
            "🔵 Other": 4,
            "⚪ Notification": 5,
            "⬜ Newsletter": 6,
        }
        email_list.sort(key=lambda x: priority_order.get(x["category"], 99))

        return email_list

    except Exception as e:
        return [{"error": f"Gmail fetch failed: {str(e)[:100]}"}]


def read_email(message_id: str) -> Optional[str]:
    """Read full content of an email by ID."""
    try:
        service = _get_service()
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        payload = msg.get("payload", {})
        parts = payload.get("parts", [])

        full_text = ""
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    full_text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        if not full_text:
            # Try body directly
            data = payload.get("body", {}).get("data", "")
            if data:
                full_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        # Get headers
        headers = payload.get("headers", [])
        subject = ""
        sender = ""
        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            elif h["name"] == "From":
                sender = h["value"]

        return f"From: {sender}\nSubject: {subject}\n\n{full_text[:3000]}"

    except Exception as e:
        return None


def draft_reply(message_id: str, reply_text: str) -> str:
    """Draft a reply to an email."""
    try:
        service = _get_service()
        original = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata")
            .execute()
        )

        # Get thread ID and headers
        thread_id = original.get("threadId", message_id)
        headers = original.get("payload", {}).get("headers", [])
        subject = ""
        to = ""
        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            elif h["name"] == "From":
                to = h["value"]

        # Create reply message
        message = EmailMessage()
        message.set_content(reply_text)
        message["To"] = to
        message["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject

        # Encode and send
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {"raw": encoded, "threadId": thread_id}

        sent = (
            service.users()
            .messages()
            .send(userId="me", body=send_body)
            .execute()
        )
        return f"Reply sent! Message ID: {sent.get('id', 'unknown')}"

    except Exception as e:
        return f"Reply draft cheyyadam lo error: {str(e)[:100]}"


def get_unread_count() -> int:
    """Get total unread email count."""
    try:
        service = _get_service()
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("messagesTotal", 0)
    except Exception:
        return 0


def check_unanswered_recruiters() -> List[str]:
    """Find recruiter emails unanswered for > 24 hours."""
    try:
        service = _get_service()
        # Search for internship-related emails from last 7 days
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q="subject:(internship OR opportunity OR interview OR role) newer_than:7d",
                maxResults=20,
            )
            .execute()
        )
        messages = results.get("messages", [])
        flags = []

        for msg in messages[:10]:
            msg_data = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = ""
            sender = ""
            date = ""
            for h in headers:
                if h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "From":
                    sender = h["value"]
                elif h["name"] == "Date":
                    date = h["value"]

            # Check if we replied (have message in same thread from us)
            thread = (
                service.users()
                .threads()
                .get(userId="me", id=msg["threadId"])
                .execute()
            )
            our_reply = False
            for thread_msg in thread.get("messages", []):
                msg_headers = thread_msg.get("payload", {}).get("headers", [])
                for h in msg_headers:
                    if h["name"] == "From" and "karthik" in h["value"].lower():
                        our_reply = True
                        break

            if not our_reply:
                # Extract sender name
                sender_name = sender.split("<")[0].strip() or sender
                flags.append(
                    f"  ⏰ {subject[:60]} — from {sender_name[:30]} — reply pending"
                )

        return flags if flags else []

    except Exception:
        return []
