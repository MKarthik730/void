"""
VOID — Project Status Tracker
Track active projects, progress, blockers in memory
"""

from typing import Optional, Dict, List
from datetime import datetime, date
from services.memory_service import add_memory, search_memories, get_context_for_query

# Known projects and their metadata
KNOWN_PROJECTS = {
    "void": {
        "name": "VOID v3.0",
        "description": "Hyper-personal AI assistant, FastAPI + LangGraph + Ollama + pgvector",
        "repo": "MKarthik730/VOID",
        "tech": ["FastAPI", "LangGraph", "PostgreSQL", "pgvector", "Ollama", "Qwen3"],
    },
    "memoir": {
        "name": "Memoir",
        "description": "Private family memory archive with AI and PDF book generation",
        "repo": "MKarthik730/Memoir",
        "tech": ["React", "Vite", "FastAPI", "PostgreSQL", "pgvector"],
    },
    "cognitus": {
        "name": "Cognitus / Cortex Council",
        "description": "Multi-agent AI reasoning platform with node-graph UI",
        "repo": "MKarthik730/Cognitus",
        "tech": ["FastAPI", "LangGraph", "Redis", "React", "TypeScript"],
    },
    "devcollab": {
        "name": "DevCollab",
        "description": "Self-hosted observability platform (like Sentry/Datadog)",
        "repo": "MKarthik730/DevCollab",
        "tech": ["Django", "React", "Vite", "Lemon Squeezy"],
    },
    "aegis": {
        "name": "Aegis",
        "description": "Family safety Android app",
        "repo": "MKarthik730/Aegis",
        "tech": ["Kotlin", "Jetpack Compose", "Firebase"],
    },
    "ai-resume-ranker": {
        "name": "AI Resume Ranker",
        "description": "5-dimension resume scoring with Gemini/Groq",
        "repo": "MKarthik730/AI-Resume-Ranker",
        "tech": ["Python", "Groq", "Gemini"],
    },
}


def update_project_status(project_name: str, field: str, value: str) -> str:
    """Update a project's status in memory.

    Args:
        project_name: Name of the project (e.g., "memoir", "cognitus")
        field: Field to update (status, pending, blocker, next_action)
        value: New value
    """
    # Validate project
    project_key = project_name.lower().replace(" ", "-")
    if project_key not in KNOWN_PROJECTS:
        # Fuzzy match
        for key, info in KNOWN_PROJECTS.items():
            if project_name.lower() in key or project_name.lower() in info["name"].lower():
                project_key = key
                break
        else:
            return f"❌ Project '{project_name}' dorakaledhu. Known: {', '.join(KNOWN_PROJECTS.keys())}"

    memory_content = f"project_status:{project_key}:{field} = {value}"
    add_memory(memory_content, category=f"project/{project_key}", importance=3)
    return f"✅ {KNOWN_PROJECTS[project_key]['name']} — {field} updated to: {value}"


def get_project_status(project_name: str) -> str:
    """Get full status of a project from memory.

    Args:
        project_name: Name of the project
    """
    # Validate project
    project_key = project_name.lower().replace(" ", "-")
    if project_key not in KNOWN_PROJECTS:
        for key, info in KNOWN_PROJECTS.items():
            if project_name.lower() in key or project_name.lower() in info["name"].lower():
                project_key = key
                break
        else:
            return f"❌ Project '{project_name}' dorakaledhu. Known: {', '.join(KNOWN_PROJECTS.keys())}"

    project = KNOWN_PROJECTS[project_key]

    # Search memory for project status
    memories = search_memories(f"project_status:{project_key}", limit=20)

    # Parse fields from memories
    fields = {"status": "🔵 Active", "pending": "Not specified", "blocker": "None", "next_action": "Not set"}
    for mem in memories:
        for field in fields:
            prefix = f"project_status:{project_key}:{field} = "
            if prefix in mem:
                fields[field] = mem.split("=", 1)[1].strip()

    result = (
        f"📊 **{project['name']}** — {fields['status']}\n"
        f"   {project['description']}\n"
        f"   🛠️ Tech: {', '.join(project['tech'])}\n"
        f"   📂 {project['repo']}\n\n"
        f"**Done:** ✓ In progress\n"
        f"**Pending:** 📋 {fields['pending']}\n"
        f"**Blocker:** ⚠️ {fields['blocker']}\n"
        f"**Next:** 🎯 {fields['next_action']}\n\n"
        f"Cheyyadam start cheyyala? 🚀"
    )

    return result


def get_all_projects_summary() -> str:
    """Get a summary of all tracked projects."""
    lines = ["📊 **All Projects**"]

    for key, project in KNOWN_PROJECTS.items():
        # Get status from memory
        memories = search_memories(f"project_status:{key}", limit=5)
        status = "🔵 Active"
        for mem in memories:
            if f"project_status:{key}:status = " in mem:
                status = mem.split("=", 1)[1].strip()
                break

        lines.append(f"\n**{project['name']}** — {status}")
        lines.append(f"   📂 {project['repo']}")

    return "\n".join(lines)


def track_session_end(session_summary: str) -> str:
    """Track what was done in a completed work session."""
    add_memory(
        f"Session completed: {session_summary}",
        category="productivity",
        importance=2,
    )
    return f"✅ Session tracked! {session_summary[:100]}"
