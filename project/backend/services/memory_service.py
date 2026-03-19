"""
VOID Backend — Memory Service (RAG with SQLite)
Persistent memory across sessions
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Tuple
import os

MEMORY_DB = os.path.join(os.path.dirname(__file__), "..", "..", "void_memory.db")


def _get_db():
    conn = sqlite3.connect(MEMORY_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_memory_db():
    """Initialize memory database tables."""
    conn = _get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding BLOB,
            category TEXT DEFAULT 'general',
            importance INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            input_data TEXT,
            output_data TEXT,
            success BOOLEAN DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")

    conn.commit()
    conn.close()


def add_conversation(user_msg: str, assistant_resp: str, context: str = None):
    """Store a conversation turn."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_message, assistant_response, context) VALUES (?, ?, ?)",
        (user_msg, assistant_resp, context),
    )
    conn.commit()
    conn.close()


def get_recent_conversations(limit: int = 10) -> List[dict]:
    """Get recent conversation history."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_memories(query: str, limit: int = 5) -> List[str]:
    """Simple keyword-based memory search."""
    conn = _get_db()
    cursor = conn.cursor()
    keywords = query.lower().split()

    if not keywords:
        return []

    conditions = " OR ".join(["content LIKE ?" for _ in keywords])
    params = [f"%{kw}%" for kw in keywords]

    cursor.execute(
        f"SELECT content FROM memories WHERE {conditions} ORDER BY importance DESC, timestamp DESC LIMIT ?",
        params + [limit],
    )
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results


def add_memory(content: str, category: str = "general", importance: int = 1):
    """Store an important memory."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (content, category, importance) VALUES (?, ?, ?)",
        (content, category, importance),
    )
    conn.commit()
    conn.close()


def get_context_for_query(
    query: str, memory_limit: int = 5, history_limit: int = 5
) -> str:
    """Get relevant context for a query."""
    memories = search_memories(query, memory_limit)
    history = get_recent_conversations(history_limit)

    context_parts = []

    if memories:
        context_parts.append("Relevant memories:")
        for m in memories:
            context_parts.append(f"- {m}")

    if history:
        context_parts.append("\nRecent conversation:")
        for h in reversed(history):
            context_parts.append(f"User: {h['user_message'][:100]}")
            context_parts.append(f"VOID: {h['assistant_response'][:100]}")

    return "\n".join(context_parts) if context_parts else ""


def log_action(
    action: str, input_data: str = None, output_data: str = None, success: bool = True
):
    """Log an action for future reference."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO action_history (action, input_data, output_data, success) VALUES (?, ?, ?, ?)",
        (action, input_data, output_data, success),
    )
    conn.commit()
    conn.close()


def get_action_history(limit: int = 20) -> List[dict]:
    """Get recent action history."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM action_history ORDER BY timestamp DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


init_memory_db()
