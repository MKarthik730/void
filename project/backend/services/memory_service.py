"""
VOID — Memory Service (pgvector RAG)
Handles DB unavailability gracefully — returns empty results when PostgreSQL is down.
"""

from typing import List, Optional
from sqlalchemy import text
from database import SessionLocal, init_db, is_db_available
from models import Conversation, Memory
from services.embedding_service import embed

# Initialize DB if possible (won't crash if PostgreSQL is down)
init_db()


def init_memory_db():
    pass


def _get_session():
    """Get a DB session or None if unavailable."""
    if not is_db_available():
        return None
    try:
        return SessionLocal()
    except Exception:
        return None


def add_conversation(user_msg: str, assistant_resp: str, context: Optional[str] = None):
    db = _get_session()
    if db is None:
        return
    try:
        db.add(
            Conversation(
                user_message=user_msg, assistant_response=assistant_resp, context=context
            )
        )
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


def get_recent_conversations(limit: int = 10) -> List[dict]:
    db = _get_session()
    if db is None:
        return []
    try:
        rows = (
            db.query(Conversation)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "user_message": r.user_message,
                "assistant_response": r.assistant_response,
                "context": r.context,
                "timestamp": str(r.created_at),
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        db.close()


def search_memories(query: str, limit: int = 5) -> List[str]:
    try:
        query_vec = embed(query)
    except Exception:
        return []

    db = _get_session()
    if db is None:
        return []
    try:
        sql = text(
            "SELECT content FROM memories "
            "WHERE embedding IS NOT NULL "
            "ORDER BY embedding <=> :query_vec "
            "LIMIT :lim"
        )
        rows = db.execute(sql, {"query_vec": query_vec, "lim": limit}).fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []
    finally:
        db.close()


def add_memory(content: str, category: str = "general", importance: int = 1):
    try:
        vector = embed(content)
    except Exception:
        vector = None

    db = _get_session()
    if db is None:
        return
    try:
        db.add(
            Memory(
                content=content, embedding=vector, category=category, importance=importance
            )
        )
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


def get_context_for_query(
    query: str, memory_limit: int = 5, history_limit: int = 5
) -> str:
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
    action: str,
    input_data: Optional[str] = None,
    output_data: Optional[str] = None,
    success: bool = True,
):
    from models import ActionLog

    db = _get_session()
    if db is None:
        return
    try:
        db.add(
            ActionLog(
                action=action,
                input_text=input_data or "",
                output_text=output_data or "",
                language="auto",
            )
        )
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


def get_action_history(limit: int = 20) -> List[dict]:
    from models import ActionLog

    db = _get_session()
    if db is None:
        return []
    try:
        rows = (
            db.query(ActionLog)
            .order_by(ActionLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "action": r.action,
                "input_text": r.input_text,
                "output_text": r.output_text,
                "timestamp": str(r.created_at),
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        db.close()
