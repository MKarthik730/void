"""
VOID — Clipboard Service
Detect clipboard content type and provide AI responses
"""

import re
from typing import Optional, Dict
from services.ollama_service import run as llm_run


def detect_content_type(text: str) -> str:
    """Detect what type of content is in the clipboard."""
    if not text or not text.strip():
        return "empty"

    text = text.strip()

    # Error message detection
    error_patterns = [
        r"Traceback \(most recent call last\)",
        r"Error:", r"Exception:", r"SyntaxError",
        r"ImportError", r"ModuleNotFoundError", r"FileNotFoundError",
        r"TypeError", r"ValueError", r"KeyError", r"AttributeError",
        r"IndexError", r"RuntimeError", r"ConnectionError",
        r"TimeoutError", r"segmentation fault", r"core dumped",
        r"failed with exit code", r"npm ERR", r"pip.*error",
        r"build failed", r"command not found",
    ]
    if any(re.search(p, text, re.IGNORECASE) for p in error_patterns):
        return "error"

    # URL detection
    url_patterns = [
        r"https?://arxiv\.org/abs/\d+",
        r"https?://arxiv\.org/pdf/\d+",
        r"https?://github\.com/[\w.-]+/[\w.-]+",
        r"https?://[\w.-]+\.\w+/\S+",
    ]
    for pattern in url_patterns:
        if re.search(pattern, text):
            url = re.search(pattern, text).group(0)
            if "arxiv" in url:
                return "arxiv"
            elif "github.com" in url:
                return "github_url"
            return "url"

    # Job description detection
    jd_patterns = [
        r"we are looking for", r"requirements?:?", r"qualifications?:?",
        r"responsibilities?:?", r"skills required", r"about the role",
        r"job description", r"internship opportunity",
    ]
    jd_score = sum(1 for p in jd_patterns if re.search(p, text, re.IGNORECASE))
    if jd_score >= 2:
        return "job_description"

    # Code snippet detection
    code_patterns = [
        r"^(import |from |def |class |function |const |let |var |fn |pub fn)",
        r"#include", r"print\(|console\.log\(|return\s",
        r"=>\s*{", r"{\s*\n\s+", r"//.*$",
    ]
    code_score = sum(1 for p in code_patterns if re.search(p, text, re.MULTILINE))
    if code_score >= 2:
        return "code"

    return "text"


def process_clipboard(text: str) -> str:
    """Process clipboard content and return AI response."""
    content_type = detect_content_type(text)

    if content_type == "empty":
        return ""

    if content_type == "error":
        return _handle_error(text)

    if content_type == "arxiv":
        from services.pdf_service import summarize_arxiv
        url_match = re.search(r"https?://arxiv\.org/\S+", text)
        if url_match:
            result = summarize_arxiv(url_match.group(0))
            return f"📋 Clipboard lo arXiv paper chusanu —\n\n{result}"
        return "📋 arXiv link dorakaledhu"

    if content_type == "url":
        url_match = re.search(r"https?://[\w.-]+\.\w+/\S+", text)
        if url_match:
            from services.pdf_service import summarize_article
            result = summarize_article(url_match.group(0))
            return f"📋 Clipboard lo article chusanu —\n\n{result}"
        return "📋 URL extract avvaledhu"

    if content_type == "job_description":
        return _analyze_jd(text)

    if content_type == "code":
        return _explain_code(text)

    # General text
    prompt = (
        "Look at this clipboard content and provide a brief summary or response.\n\n"
        f"{text[:1000]}"
    )
    result = llm_run(prompt, max_tokens=200)
    if result.startswith("ERROR"):
        return f"📋 Clipboard lo text chusanu — but summarize cheyyadam raledhu"
    return f"📋 Clipboard lo text chusanu —\n{result}"


def _handle_error(error_text: str) -> str:
    """Analyze an error message and suggest a fix."""
    prompt = (
        "Analyze this error message. Explain the cause and provide a fix.\n"
        "Format:\nCause: [brief cause in English]\nFix: [copy-paste ready fix]\n\n"
        f"Error:\n{error_text[:1500]}"
    )
    result = llm_run(prompt, max_tokens=300)
    if result.startswith("ERROR"):
        return f"📋 Clipboard lo error chusanu — but analyze cheyyadam raledhu bro"
    return f"📋 Clipboard lo error chusanu —\n{result}"


def _analyze_jd(text: str) -> str:
    """Analyze a job description and match against Karthik's profile."""
    prompt = (
        "Analyze this job description for a 19-year-old CSE student named Karthik. "
        "Score the match from 1-10 and explain why. "
        "Highlight which of his skills match and which are missing.\n"
        "His skills: Python, FastAPI, React, TypeScript, LangGraph, "
        "PostgreSQL, pgvector, Docker, Redis, LightGBM, CatBoost.\n"
        "Format:\nMatch Score: X/10\nMatching Skills: ...\nGaps: ...\n\n"
        f"Job Description:\n{text[:2000]}"
    )
    result = llm_run(prompt, max_tokens=300)
    if result.startswith("ERROR"):
        return f"📋 JD analysis failed bro — manual ga check cheyyi"
    return f"📋 Clipboard lo JD chusanu — apply cheyyala?\n{result}"


def _explain_code(code: str) -> str:
    """Explain a code snippet and suggest improvements."""
    prompt = (
        "Explain what this code does in 2-3 sentences. "
        "Then suggest 1 improvement.\n\n"
        f"{code[:1500]}"
    )
    result = llm_run(prompt, max_tokens=200)
    if result.startswith("ERROR"):
        return f"📋 Code chusanu but explain cheyyadam raledhu"
    return f"📋 Clipboard lo code chusanu —\n{result}"
