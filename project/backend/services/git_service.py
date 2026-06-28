"""
VOID — Git Service
Auto-commit messages, diff analysis, security key detection
"""

import subprocess
import re
import os
from typing import List, Optional
from services.ollama_service import run as llm_run

# Patterns that look like API keys / secrets
SECRET_PATTERNS = [
    # OpenAI
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
    # Google
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    # Groq
    (r"gsk_[a-zA-Z0-9]{40,}", "Groq API Key"),
    # GitHub
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"github_pat_[a-zA-Z0-9]{85}", "GitHub Fine-Grained Token"),
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    # Generic
    (r"-----BEGIN RSA PRIVATE KEY-----", "RSA Private Key"),
    (r"-----BEGIN OPENSSH PRIVATE KEY-----", "SSH Private Key"),
    (r"-----BEGIN PRIVATE KEY-----", "Private Key"),
    # JWT
    (r"eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}", "JWT Token"),
    # Stripe
    (r"sk_live_[a-zA-Z0-9]{20,}", "Stripe Live Secret Key"),
    (r"pk_live_[a-zA-Z0-9]{20,}", "Stripe Live Publishable Key"),
    # Generic secret
    (r"(?:api[_-]?key|apikey|secret|token|password)\s*[=:]\s*['\"][^'\"]{16,}['\"]", "Potential Secret (check manually)"),
]

KNOWN_SENSITIVE_FILES = [
    ".env", ".env.*", "credentials.json", "token.json",
    "*.pem", "*.key", "id_rsa", "id_rsa.pub",
    "service-account.json", "service_account.json",
    "config.py",  # if keys are hardcoded
]


def get_diff() -> str:
    """Get git diff of staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.join(os.path.dirname(__file__), "..", "..", ".."),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        # If nothing staged, get unstaged diff
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.join(os.path.dirname(__file__), "..", "..", ".."),
        )
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def scan_for_secrets(diff: str = None) -> List[str]:
    """Scan diff for exposed API keys and secrets."""
    if diff is None:
        diff = get_diff()

    if not diff:
        return []

    warnings = []

    # Check for secret patterns
    for pattern, secret_type in SECRET_PATTERNS:
        matches = re.findall(pattern, diff, re.IGNORECASE)
        if matches:
            # Find which file
            lines = diff.split("\n")
            current_file = "unknown"
            for line in lines:
                if line.startswith("+++ b/"):
                    current_file = line[6:]
                for match in matches:
                    # Mask the secret in the warning
                    masked = match[:6] + "..." + match[-4:] if len(match) > 20 else match[:8] + "..."
                    if masked in line:
                        warnings.append(
                            f"⚠️ **{secret_type}** exposed in `{current_file}` — "
                            f"masked: `{masked}`"
                        )

    # Check for sensitive files being committed
    for pattern in KNOWN_SENSITIVE_FILES:
        pattern_regex = pattern.replace(".", r"\.").replace("*", ".*")
        if re.search(f"\\+\\+\\+ b/{pattern_regex}", diff):
            warnings.append(
                f"⚠️ Sensitive file `{pattern}` in diff — sure you want to commit this?"
            )

    return warnings


def generate_commit_message(diff: str = None) -> str:
    """Generate a conventional commit message from diff."""
    if diff is None:
        diff = get_diff()

    if not diff or len(diff) < 10:
        return "No changes detected bro"

    # Truncate for LLM
    diff_preview = diff[:2000]

    prompt = (
        "Generate a conventional commit message from this git diff.\n"
        "Format: type(scope): description\n\n"
        "Types: feat, fix, refactor, docs, chore, perf, test, style\n\n"
        "Rules:\n"
        "- Max 72 chars for the title\n"
        "- Short description (1 line)\n"
        "- No body needed\n\n"
        f"Diff:\n{diff_preview}"
    )

    result = llm_run(prompt, max_tokens=80, temperature=0.3)
    if result.startswith("ERROR"):
        # Fallback: extract from diff
        lines = diff.split("\n")
        added = [l for l in lines if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in lines if l.startswith("-") and not l.startswith("---")]

        type_guess = "feat" if added else "fix"
        files = [l[6:] for l in lines if l.startswith("+++ b/")]
        scope = files[0].split("/")[0] if files else "general"
        desc = f"{len(added)} additions, {len(removed)} deletions"

        return f"{type_guess}({scope}): {desc}"

    return result.strip()


def check_before_push() -> str:
    """Full security check before git push. Returns warnings or 'safe'."""
    diff = get_diff()
    if not diff:
        return "No changes to push bro"

    secrets = scan_for_secrets(diff)
    if secrets:
        warning_text = "\n".join(secrets)
        return (
            f"⚠️ **WAIT BRO — Security issues detected!** ⚠️\n\n"
            f"{warning_text}\n\n"
            f"DO NOT PUSH. Fix these first:\n"
            f"1. Add to .gitignore\n"
            f"2. Rotate exposed keys immediately\n"
            f"3. Use environment variables instead\n"
            f"4. Remove from git history with 'git rm --cached'"
        )

    # Check if .gitignore exists and has .env
    try:
        gitignore_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", ".gitignore"
        )
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                content = f.read()
            if ".env" not in content:
                return (
                    "⚠️ Bro, .env file .gitignore lo ledhu!\n"
                    "Add .env to .gitignore before push!"
                )
    except Exception:
        pass

    commit_msg = generate_commit_message(diff)
    return f"✅ Security check passed — safe to push.\n\nSuggested commit:\n`{commit_msg}`"
