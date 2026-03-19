"""
VOID Backend — Simple Agentic Core
Direct Ollama API with tool-like behavior
"""

import json
import re
from services.ollama_service import run as llm_run
from services.memory_service import (
    get_context_for_query,
    add_conversation,
    add_memory,
    log_action,
)

SYSTEM_PROMPT = """You are VOID, a friendly AI assistant that speaks in Tenglish.

Tenglish = Telugu words written in English script mixed with English naturally.
Casual words: bro, ra, rey, kada, ga, ani, undi, cheppu, nenu, ela, em, ayyo

You have these capabilities:
- Screen analysis (summarize, explain, translate)
- Memory (remember facts, recall past conversations)
- Desktop actions (screenshot, type text)
- General conversation

Keep responses conversational, short, and in Tenglish style."""

TOOL_DESCRIPTIONS = """
Available tools:
- analyze_screen: Analyze a screenshot (actions: summarize, explain, translate, suggest)
- describe_screen: Describe what's on screen
- remember: Store important facts
- recall: Retrieve relevant memories
- execute_action: Execute desktop actions (screenshot, minimize, close_tab)
"""


def run_agent(user_input: str) -> str:
    """Simple agent that decides what to do based on user input."""

    context = get_context_for_query(user_input, memory_limit=3, history_limit=3)

    intent_prompt = f"""Analyze this user request and determine what to do:
User: {user_input}

Respond with ONLY a JSON object like this (no extra text):
{{"action": "chat", "reasoning": "brief reason"}}

action can be: chat, recall_memory, remember, analyze_screen, describe_screen
"""

    intent_result = llm_run(intent_prompt, max_tokens=100)

    try:
        intent = (
            json.loads(intent_result)
            if intent_result.startswith("{")
            else {"action": "chat"}
        )
    except:
        intent = {"action": "chat"}

    action = intent.get("action", "chat")

    if action == "recall_memory":
        result = get_context_for_query(user_input, memory_limit=5, history_limit=5)
        if result:
            return f"From my memory:\n{result[:500]}"
        return "I don't have specific memories about that yet. But I can help you with whatever you're working on!"

    elif action == "remember":
        key_fact = user_input
        add_memory(key_fact, category="general", importance=2)
        return f"Got it bro, I'll remember that! {key_fact[:100]}"

    else:
        response_prompt = f"""{SYSTEM_PROMPT}

{TOOL_DESCRIPTIONS}

{("Relevant context:\n" + context) if context else ""}

Conversation history (recent):
{get_context_for_query(user_input, memory_limit=0, history_limit=5)}

User: {user_input}

Respond in Tenglish style, keeping it conversational and helpful. If asking about past actions, reference memory. Max 3 sentences."""

        response = llm_run(response_prompt, max_tokens=300, temperature=0.8)

        if not response.startswith("ERROR"):
            add_conversation(user_input, response, context)

        return response


def run_simple(prompt: str) -> str:
    """Direct LLM call without agent logic."""
    return llm_run(prompt, max_tokens=300)
