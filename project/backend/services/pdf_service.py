"""
VOID — PDF/Paper Service
Summarize PDFs and arXiv papers
"""

from typing import Optional
import requests
import os
import tempfile


def summarize_pdf(file_path: str) -> str:
    """Summarize a local PDF file using pymupdf + Ollama."""
    try:
        import fitz  # pymupdf
    except ImportError:
        return "pymupdf install cheyyaledhu bro — pip install pymupdf"

    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        if not text.strip():
            return "PDF lo text emi levu bro — it might be scanned images"

        # Truncate for LLM context
        text = text[:3000]

        from services.ollama_service import run
        prompt = (
            "Summarize this document in 5 bullet points. "
            "Focus on key findings, methods, and conclusions.\n\n"
            f"{text}"
        )
        result = run(prompt, max_tokens=400)
        return result if not result.startswith("ERROR") else "Summarize cheyyadam lo issue vachindi bro"

    except Exception as e:
        return f"PDF read cheyyadam lo error: {str(e)[:100]}"


def summarize_arxiv(url: str) -> str:
    """Summarize an arXiv paper from URL."""
    # arXiv abstract page
    try:
        # Convert to abstract page if it's a PDF link
        if "/pdf/" in url:
            url = url.replace("/pdf/", "/abs/")
            url = url.replace(".pdf", "")

        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; VOID/3.0)"
        })
        resp.raise_for_status()

        # Extract title + abstract from HTML
        html = resp.text
        title = ""
        abstract = ""

        # Simple HTML extraction (works for arXiv)
        if "<title>" in html:
            title = html.split("<title>")[1].split("</title>")[0].strip()

        if "<blockquote class="abstract"" in html:
            abstract_part = html.split('<blockquote class="abstract"')[1]
            abstract = abstract_part.split(">", 1)[1].split("</blockquote>")[0]
            # Strip HTML tags
            import re
            abstract = re.sub(r'<[^>]+>', '', abstract).strip()
        elif "<meta name="citation_abstract"" in html:
            import re
            match = re.search(r'<meta name="citation_abstract"[^>]*content="([^"]+)"', html)
            if match:
                abstract = match.group(1)

        if not abstract:
            return "Abstract extract cheyyadam raledhu bro — manual ga check cheyyi"

        # Truncate for LLM
        abstract = abstract[:2000]

        from services.ollama_service import run
        prompt = (
            "Summarize this arXiv paper abstract in 5 bullet points. "
            "For each point, mention how it could be used in a real project "
            "(especially for an AI agent platform called Cognitus).\n\n"
            f"Title: {title}\n\n{abstract}"
        )
        result = run(prompt, max_tokens=400)

        if result.startswith("ERROR"):
            return f"📄 {title}\n\n{abstract[:500]}...\n\n(LLM summary failed, raw abstract above)"

        return f"📄 **{title}**\n\n{result}"

    except requests.RequestException:
        return "arXiv fetch avvaledhu bro — URL correct aa check cheyyi"
    except Exception as e:
        return f"Error processing arXiv paper: {str(e)[:100]}"


def summarize_article(url: str) -> str:
    """Summarize any article from URL."""
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; VOID/3.0)"
        })
        resp.raise_for_status()

        html = resp.text
        import re
        # Extract text from <p> tags (simple approach)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        text = " ".join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if p.strip())

        if not text:
            # Fallback: try to get anything readable
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()[:2000]

        text = text[:3000]

        from services.ollama_service import run
        prompt = (
            "Summarize this article in 4-5 bullet points. Be concise.\n\n"
            f"{text}"
        )
        result = run(prompt, max_tokens=400)
        return result if not result.startswith("ERROR") else "Article summarize cheyyadam lo issue vachindi bro"

    except Exception as e:
        return f"Article fetch avvaledhu: {str(e)[:100]}"
