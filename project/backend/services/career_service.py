"""
VOID — Career Service
Internship tracking, JD matching, cold email drafts
"""

from typing import Optional, List, Dict
from datetime import datetime, date
from services.memory_service import add_memory, search_memories
from services.ollama_service import run as llm_run


def track_application(company: str, role: str, status: str = "applied", notes: str = "") -> str:
    """Track a job/internship application in memory.

    Args:
        company: Company name
        role: Role title
        status: Applied, Interview, Rejected, Offer, etc.
        notes: Optional notes
    """
    timestamp = datetime.now().strftime("%b %d, %Y")
    memory_content = (
        f"application:{company.lower()}:{role.lower()} = "
        f"Company: {company}, Role: {role}, Status: {status}, "
        f"Date: {timestamp}, Notes: {notes}"
    )
    add_memory(memory_content, category="career", importance=3)
    return f"✅ Application tracked: {company} — {role} ({status})"


def get_application_status() -> str:
    """Get summary of all tracked applications."""
    memories = search_memories("application:", limit=30)

    if not memories:
        return "🎯 No applications tracked yet bro. Start applying!"

    applications = []
    for mem in memories:
        parts = mem.split(" = ", 1)
        if len(parts) == 2:
            data = parts[1]
            company = ""
            role = ""
            status = ""
            date_str = ""
            for item in data.split(", "):
                if item.startswith("Company:"):
                    company = item.split(": ", 1)[1]
                elif item.startswith("Role:"):
                    role = item.split(": ", 1)[1]
                elif item.startswith("Status:"):
                    status = item.split(": ", 1)[1]
                elif item.startswith("Date:"):
                    date_str = item.split(": ", 1)[1]

            if company and role:
                applications.append({
                    "company": company,
                    "role": role,
                    "status": status,
                    "date": date_str,
                })

    if not applications:
        return "🎯 No applications parsed from memory yet bro"

    # Count by status
    status_counts = {}
    for app in applications:
        s = app["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    lines = [f"🎯 **Career Tracker** — {len(applications)} total applications"]
    lines.append(f"   Status: {', '.join(f'{k}: {v}' for k, v in status_counts.items())}")
    lines.append("")

    # Show recent 5
    lines.append("**Recent Applications:**")
    for app in applications[-5:]:
        emoji = {
            "applied": "📤",
            "interview": "🎯",
            "rejected": "❌",
            "offer": "🎉",
            "screening": "⏳",
        }.get(app["status"].lower(), "📋")
        lines.append(f"  {emoji} {app['company']} — {app['role']} ({app['status']})")

    return "\n".join(lines)


def analyze_jd(jd_text: str) -> str:
    """Analyze a job description and provide match score.

    Args:
        jd_text: Full job description text
    """
    prompt = (
        "You are a career advisor for a 19-year-old CSE student named Karthik. "
        "Analyze this job description and:\n"
        "1. Score the match from 1-10\n"
        "2. List matching skills\n"
        "3. List gaps or missing skills\n"
        "4. Suggest which projects to highlight from: Memoir, Cognitus, DevCollab, VOID, Aegis\n"
        "5. Give 1 specific action tip\n\n"
        f"Karthik's skills: Python, FastAPI, React, TypeScript, LangGraph, "
        f"PostgreSQL, pgvector, Docker, Redis, LightGBM, CatBoost, AutoGluon, Optuna, Polars\n\n"
        f"Job Description:\n{jd_text[:2500]}"
    )
    result = llm_run(prompt, max_tokens=400, temperature=0.3)
    if result.startswith("ERROR"):
        return "JD analysis failed bro — Ollama running aa?"
    return f"🎯 **JD Analysis**\n\n{result}"


def generate_draft_email(company: str, role: str, style: str = "cold") -> str:
    """Generate a draft email for internship application.

    Args:
        company: Company name
        role: Role title
        style: 'cold' for cold email, 'followup' for follow-up
    """
    if style == "followup":
        prompt = (
            f"Draft a follow-up email for {company} regarding a {role} application. "
            f"Keep it professional but not stiff. Short and direct. "
            f"Karthik is a 2nd year CSE student at ANITS Visakhapatnam. "
            f"He has experience with Python, FastAPI, React, TypeScript, and AI/ML. "
            f"His notable projects include VOID (AI assistant), Memoir (family archive), and Cognitus (multi-agent platform)."
        )
    else:
        prompt = (
            f"Draft a cold email to {company} applying for the {role} position. "
            f"Keep it professional but not stiff. Short and direct. "
            f"Karthik is a 2nd year CSE student at ANITS Visakhapatnam. "
            f"He has experience with Python, FastAPI, React, TypeScript, and AI/ML. "
            f"His notable projects include VOID (AI assistant), Memoir (family archive), and Cognitus (multi-agent platform). "
            f"Attach GitHub: github.com/MKarthik730"
        )

    result = llm_run(prompt, max_tokens=300, temperature=0.5)
    if result.startswith("ERROR"):
        return "Draft generation failed bro — Ollama running aa?"
    return f"📧 **Draft Email for {company} — {role}**\n\n{result}"


def suggest_platforms() -> str:
    """Suggest platforms to apply on."""
    return (
        "🎯 **Recommended Platforms** (priority order)\n\n"
        "1. **Internshala** — best for Indian internships, active recruiter base\n"
        "2. **Unstop** — hackathons + internships + competitions\n"
        "3. **LinkedIn** — network + easy apply, optimize profile first\n"
        "4. **WellFound** — (formerly AngelList) startups, good for dev roles\n"
        "5. **YC Work at a Startup** — YC-backed startups, high quality\n"
        "6. **HackerNews: Who's Hiring** — monthly thread, top-tier\n\n"
        "Tip: Apply to 5-10/week for consistent pipeline bro!"
    )


def track_interview(company: str, date_str: str, notes: str = "") -> str:
    """Track an upcoming interview.

    Args:
        company: Company name
        date_str: Interview date/time
        notes: Preparation notes
    """
    memory_content = (
        f"interview:{company.lower()} = "
        f"Company: {company}, Date: {date_str}, Status: upcoming, Notes: {notes}"
    )
    add_memory(memory_content, category="career", importance=4)

    return (
        f"🎯 **Interview tracked!**\n"
        f"   Company: {company}\n"
        f"   Date: {date_str}\n"
        f"   Notes: {notes}\n\n"
        f"Prep tip: Research company, practice common problems, prepare questions for them bro!"
    )
