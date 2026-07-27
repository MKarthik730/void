# -*- coding: utf-8 -*-
"""
VOID — Project Scaffold Service
LLM-powered project planning + execution with idiomatic boilerplate generation.
Uses Ollama (Qwen3:8b) to turn natural language descriptions into ordered file plans.
"""

import json
import re
from typing import List, Optional, Dict, Any

from services.ollama_service import run as llm_run
from services.file_service import (
    create_file,
    create_directory,
    create_project_structure,
    is_destructive,
    FileActionError,
)
from services.memory_service import log_action

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 PLAN STEP SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

VALID_STEP_TYPES = {"mkdir", "create_file", "write_file", "git_init"}

STEP_SCHEMA = {
    "type": {"required": True, "type": str, "values": VALID_STEP_TYPES},
    "path": {"required": True, "type": str},
    "content": {"required": False, "type": (str, type(None))},
    "mode": {"required": False, "type": str, "values": {"overwrite", "append"}},
}


def _validate_plan(plan: List[dict]) -> List[str]:
    """Validate a plan against the step schema. Returns list of error messages.

    Returns empty list if valid.
    """
    errors = []
    if not isinstance(plan, list):
        return ["Plan should be a list bro — JSON array expect chestunnanu"]

    for i, step in enumerate(plan):
        if not isinstance(step, dict):
            errors.append(f"Step {i}: dictionary expect chesanu, got {type(step).__name__}")
            continue

        step_type = step.get("type", "")
        if step_type not in VALID_STEP_TYPES:
            errors.append(
                f"Step {i}: '{step_type}' valid kaadhu bro. "
                f"Use one of: {', '.join(sorted(VALID_STEP_TYPES))}"
            )

        path = step.get("path", "")
        if not path or not isinstance(path, str):
            errors.append(f"Step {i}: 'path' required and must be a string bro")

        content = step.get("content")
        if content is not None and not isinstance(content, str):
            errors.append(f"Step {i}: 'content' should be string or null bro")

        # git_init should not have content
        if step_type == "git_init" and content:
            errors.append(f"Step {i}: git_init ki content ivvakandi bro — adi auto chestundi")

    return errors


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 LLM PROMPT WITH FEW-SHOT EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

PLANNER_SYSTEM_PROMPT = """You are VOID's project scaffolding engine. You take natural language descriptions of a project and output a structured JSON plan of file/folder operations.

You MUST output ONLY a JSON array of step objects. No markdown, no explanation, no extra text.

Each step object has:
- "type": "mkdir" | "create_file" | "git_init"
- "path": relative path string (no leading slash, use forward slashes)
- "content": file content string (for create_file steps), or null

Rules:
- ALL paths are relative to the project root directory (which will be auto-created)
- For mkdir, content must be null
- For git_init, content must be null
- Write COMPLETE, production-ready boilerplate code, not stubs
- Add descriptive README.md at the project root
- Include requirements.txt with relevant dependencies
- For Python projects, include a main entry point file
- For web projects, include a basic HTML/index file
- Keep content concise but complete — enough to be immediately runnable

FEW-SHOT EXAMPLES:

Input: "create a FastAPI backend project called expense-tracker"
Output:
[
  {"type": "mkdir", "path": "expense-tracker", "content": null},
  {"type": "mkdir", "path": "expense-tracker/app", "content": null},
  {"type": "create_file", "path": "expense-tracker/requirements.txt", "content": "fastapi\\nuvicorn\\npydantic\\nsqlalchemy\\npython-dotenv"},
  {"type": "create_file", "path": "expense-tracker/app/__init__.py", "content": "# Expense Tracker API"},
  {"type": "create_file", "path": "expense-tracker/app/main.py", "content": "from fastapi import FastAPI\\n\\napp = FastAPI(title=\\"Expense Tracker\\")\\n\\n\\n@app.get(\\"/\\")\\ndef root():\\n    return {\\"message\\": \\"Expense Tracker API\\"}\\n\\n\\n@app.get(\\"/health\\")\\ndef health():\\n    return {\\"status\\": \\"ok\\"}\\n"},
  {"type": "create_file", "path": "expense-tracker/app/models.py", "content": "from pydantic import BaseModel\\nfrom typing import Optional\\nfrom datetime import datetime\\n\\n\\nclass Expense(BaseModel):\\n    id: Optional[int] = None\\n    amount: float\\n    category: str\\n    description: str = \\"\\"\\n    date: datetime = datetime.now()\\n"},
  {"type": "create_file", "path": "expense-tracker/README.md", "content": "# Expense Tracker\\n\\nA FastAPI-based expense tracking application.\\n\\n## Setup\\n\\n```bash\\npip install -r requirements.txt\\nuvicorn app.main:app --reload\\n```\\n"},
  {"type": "create_file", "path": "expense-tracker/.gitignore", "content": "__pycache__/\\n*.pyc\\n.env\\nvenv/\\n.venv/\\n*.db\\n"},
  {"type": "git_init", "path": "expense-tracker", "content": null}
]

Input: "create a React frontend called my-dashboard"
Output:
[
  {"type": "mkdir", "path": "my-dashboard", "content": null},
  {"type": "mkdir", "path": "my-dashboard/src", "content": null},
  {"type": "mkdir", "path": "my-dashboard/public", "content": null},
  {"type": "create_file", "path": "my-dashboard/package.json", "content": "{\\"name\\": \\"my-dashboard\\", \\"version\\": \\"1.0.0\\", \\"private\\": true, \\"scripts\\": {\\"dev\\": \\"vite\\", \\"build\\": \\"vite build\\", \\"preview\\": \\"vite preview\\"}, \\"dependencies\\": {\\"react\\": \\"^18.2.0\\", \\"react-dom\\": \\"^18.2.0\\"}, \\"devDependencies\\": {\\"vite\\": \\"^5.0.0\\", \\"@vitejs/plugin-react\\": \\"^4.2.0\\"}}"},
  {"type": "create_file", "path": "my-dashboard/index.html", "content": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>\\n  <meta charset=\\"UTF-8\\"/>\\n  <meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1.0\\"/>\\n  <title>My Dashboard</title>\\n</head>\\n<body>\\n  <div id=\\"root\\"></div>\\n  <script type=\\"module\\" src=\\"/src/main.jsx\\"></script>\\n</body>\\n</html>"},
  {"type": "create_file", "path": "my-dashboard/src/main.jsx", "content": "import React from 'react'\\nimport ReactDOM from 'react-dom/client'\\nimport App from './App'\\n\\nReactDOM.createRoot(document.getElementById('root')).render(\\n  <React.StrictMode>\\n    <App />\\n  </React.StrictMode>\\n)"},
  {"type": "create_file", "path": "my-dashboard/src/App.jsx", "content": "function App() {\\n  return (\\n    <div>\\n      <h1>My Dashboard</h1>\\n      <p>Welcome bro! 🚀</p>\\n    </div>\\n  )\\n}\\n\\nexport default App"},
  {"type": "create_file", "path": "my-dashboard/vite.config.js", "content": "import { defineConfig } from 'vite'\\nimport react from '@vitejs/plugin-react'\\n\\nexport default defineConfig({\\n  plugins: [react()],\\n})"},
  {"type": "create_file", "path": "my-dashboard/README.md", "content": "# My Dashboard\\n\\nReact dashboard built with Vite.\\n\\n```bash\\nnpm install\\nnpm run dev\\n```"},
  {"type": "git_init", "path": "my-dashboard", "content": null}
]

Input: "create a Python CLI tool called file-sorter"
Output:
[
  {"type": "mkdir", "path": "file-sorter", "content": null},
  {"type": "mkdir", "path": "file-sorter/file_sorter", "content": null},
  {"type": "create_file", "path": "file-sorter/requirements.txt", "content": "click\\npathlib"},
  {"type": "create_file", "path": "file-sorter/file_sorter/__init__.py", "content": "\"\"\"File Sorter — organize files by extension.\"\"\"\\n__version__ = \\"1.0.0\\""},
  {"type": "create_file", "path": "file-sorter/file_sorter/cli.py", "content": "import click\\nfrom pathlib import Path\\n\\n\\n@click.command()\\n@click.argument(\\"directory\\", type=click.Path(exists=True))\\n@click.option(\\"--dry-run\\", is_flag=True, help=\\"Show what would be done\\")\\ndef sort_files(directory, dry_run):\\n    \\"\\"\\"Sort files in DIRECTORY by extension.\\"\\"\\"\\n    base = Path(directory)\\n    click.echo(f\\"Sorting {base}...\\")\\n    for f in base.iterdir():\\n        if f.is_file() and not f.name.startswith('.'):\\n            ext = f.suffix[1:] or 'no_ext'\\n            target = base / ext\\n            if not dry_run:\\n                target.mkdir(exist_ok=True)\\n                f.rename(target / f.name)\\n                click.echo(f\\"  Moved {f.name} -> {ext}/\\")\\n            else:\\n                click.echo(f\\"  Would move {f.name} -> {ext}/\\")\\n\\n\\nif __name__ == \\"__main__\\":\\n    sort_files()"},
  {"type": "create_file", "path": "file-sorter/setup.py", "content": "from setuptools import setup, find_packages\\n\\nsetup(\\n    name=\\"file-sorter\\",\\n    version=\\"1.0.0\\",\\n    packages=find_packages(),\\n    install_requires=[\\"click\\"],\\n    entry_points={\\"console_scripts\\": [\\"file-sorter=file_sorter.cli:sort_files\\"]},\\n)"},
  {"type": "create_file", "path": "file-sorter/README.md", "content": "# File Sorter\\n\\nCLI tool to organize files by extension.\\n\\n```bash\\npip install -e .\\nfile-sorter /path/to/directory\\nfile-sorter /path/to/directory --dry-run\\n```"},
  {"type": "git_init", "path": "file-sorter", "content": null}
]
"""


def plan_project(description: str, max_retries: int = 1) -> List[Dict[str, Any]]:
    """Generate a project scaffolding plan from a natural language description.

    Args:
        description: Natural language description of the project to create
        max_retries: Number of times to retry if JSON validation fails

    Returns:
        List of plan step dicts, or raises FileActionError on failure
    """
    prompt = (
        f"Generate a JSON array of file/folder operations for this project request:\\n\\n"
        f"Input: \"{description}\"\\n\\n"
        f"Output ONLY the JSON array, no other text:"
    )

    for attempt in range(max_retries + 1):
        try:
            raw = llm_run(prompt, system=PLANNER_SYSTEM_PROMPT, max_tokens=3000, temperature=0.3)

            if raw.startswith("ERROR"):
                raise FileActionError(
                    f"LLM plan generation failed: {raw}",
                    action="plan_project",
                    path="",
                )

            # Strip markdown code fences if present
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            # Find first [ and last ]
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1:
                cleaned = cleaned[start:end + 1]

            plan = json.loads(cleaned)

            # Validate schema
            errors = _validate_plan(plan)
            if not errors:
                log_action("scaffold_plan", description, f"Generated {len(plan)} steps")
                return plan

            if attempt < max_retries:
                # Retry with error feedback
                prompt = (
                    f"Your previous response had validation errors. Fix them and retry.\\n\\n"
                    f"Errors:\\n{chr(10).join(errors)}\\n\\n"
                    f"Original request: {description}\\n\\n"
                    f"Output ONLY the corrected JSON array:"
                )
            else:
                raise FileActionError(
                    f"Plan validation failed after {max_retries + 1} attempts: {'; '.join(errors[:3])}",
                    action="plan_project",
                    path="",
                )

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                prompt = (
                    f"Your response was not valid JSON. Error: {e}\\n\\n"
                    f"Original request: {description}\\n\\n"
                    f"Output ONLY valid JSON array:"
                )
            else:
                raise FileActionError(
                    f"Plan JSON parse failed after {max_retries + 1} attempts: {e}",
                    action="plan_project",
                    path="",
                )
        except FileActionError:
            raise
        except Exception as e:
            raise FileActionError(str(e)[:200], action="plan_project", path="")

    # Should not reach here, but safety net
    raise FileActionError("Plan generation failed — unexpected flow bro", action="plan_project", path="")


def execute_plan(plan: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute a project scaffolding plan step by step.

    Args:
        plan: List of step dicts with type, path, content keys

    Returns:
        Dict with keys: results (list of step result dicts), failed_step (int or None),
        all_success (bool), total_steps (int), completed_steps (int)
    """
    results = []
    failed_step = None

    for i, step in enumerate(plan):
        step_type = step.get("type", "")
        step_path = step.get("path", "")
        step_content = step.get("content", "")
        step_mode = step.get("mode", "overwrite")

        try:
            if step_type == "mkdir":
                result = create_directory(step_path)
            elif step_type == "create_file":
                result = create_file(step_path, step_content or "")
            elif step_type == "write_file":
                from services.file_service import write_file
                result = write_file(step_path, step_content or "", mode=step_mode)
            elif step_type == "git_init":
                result = _git_init(step_path)
            else:
                result = {
                    "action": "unknown",
                    "path": step_path,
                    "success": False,
                    "error": f"Unknown step type: {step_type}",
                }

            results.append(result)

            if not result.get("success", False):
                failed_step = i
                break

        except FileActionError as e:
            results.append(e.to_dict())
            failed_step = i
            break
        except Exception as e:
            results.append({
                "action": step_type,
                "path": step_path,
                "success": False,
                "error": str(e)[:200],
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            })
            failed_step = i
            break

    all_success = failed_step is None

    result_data = {
        "results": results,
        "failed_step": failed_step,
        "all_success": all_success,
        "total_steps": len(plan),
        "completed_steps": len(results),
    }

    log_action(
        "scaffold_execute",
        f"{len(plan)} steps",
        f"Success: {all_success}, Completed: {len(results)}/{len(plan)}",
        success=all_success,
    )

    return result_data


def _git_init(path: str) -> dict:
    """Initialize a git repository at the given path.

    Args:
        path: Project path relative to workspace root

    Returns:
        Structured result dict
    """
    import subprocess
    from pathlib import Path
    import config

    try:
        # Resolve path relative to the first workspace root
        workspace_root = Path(config.FILE_WORKSPACE_ROOTS.split(";")[0].strip()).expanduser().resolve()
        resolved = (workspace_root / path).resolve()
        if not resolved.exists():
            return {
                "action": "git_init",
                "path": path,
                "success": False,
                "error": f"Path ledhu bro: {path}. mkdir step mundu raavali.",
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }

        # Check if git is available
        try:
            subprocess.run(["git", "--version"], capture_output=True, timeout=5)
        except (subprocess.SubprocessError, FileNotFoundError):
            return {
                "action": "git_init",
                "path": path,
                "success": False,
                "error": "Git install avvaledhu bro — 'git init' manual ga cheyyi.",
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }

        # Check if already a git repo
        existing = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=10,
        )
        if existing.returncode == 0:
            return {
                "action": "git_init",
                "path": path,
                "success": True,
                "note": "Already a git repo bro",
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }

        result = subprocess.run(
            ["git", "-C", str(resolved), "init"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            # Create initial commit
            subprocess.run(
                ["git", "-C", str(resolved), "add", "-A"],
                capture_output=True, timeout=10,
            )
            subprocess.run(
                ["git", "-C", str(resolved), "commit", "-m", "Initial commit — scaffolded by VOID 🚀"],
                capture_output=True, timeout=10,
            )
            return {
                "action": "git_init",
                "path": path,
                "success": True,
                "note": "Git repo initialized with initial commit",
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }
        else:
            return {
                "action": "git_init",
                "path": path,
                "success": False,
                "error": result.stderr[:200],
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }

    except FileActionError:
        raise
    except Exception as e:
        return {
            "action": "git_init",
            "path": path,
            "success": False,
            "error": str(e)[:200],
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }


def format_plan_for_response(plan: List[Dict[str, Any]]) -> str:
    """Format a plan into a human-readable Tenglish response.

    Args:
        plan: List of plan step dicts

    Returns:
        Formatted string showing all planned steps
    """
    if not plan:
        return "Plan empty bro — emi cheyyalo cheppaledhu."

    lines = [f"📋 **Project Plan** — {len(plan)} steps"]
    for i, step in enumerate(plan, 1):
        step_type = step.get("type", "?")
        step_path = step.get("path", "?")
        emoji = {"mkdir": "📁", "create_file": "📄", "write_file": "✏️", "git_init": "🔗"}.get(step_type, "➡️")
        content_preview = ""
        if step.get("content"):
            content_preview = f" ({len(step['content'])} chars)"
        lines.append(f"  {emoji} `{step_path}`{content_preview}")

    return "\n".join(lines)


def format_execution_results(execution_result: Dict[str, Any], description: str) -> str:
    """Format execution results into a Tenglish response for the user.

    Args:
        execution_result: Result dict from execute_plan()
        description: Original project description

    Returns:
        Friendly Tenglish summary string
    """
    results = execution_result.get("results", [])
    all_success = execution_result.get("all_success", False)
    total = execution_result.get("total_steps", 0)
    completed = execution_result.get("completed_steps", 0)

    if all_success:
        # Count by type
        mkdirs = sum(1 for r in results if r.get("action") == "create_directory")
        files = sum(1 for r in results if r.get("action") in ("create_file", "write_file"))
        git = sum(1 for r in results if r.get("action") == "git_init")

        lines = [
            f"🚀 **{description}** — Done bro! 🔥",
            "",
            f"  📁 {mkdirs} directories created" if mkdirs else "",
            f"  📄 {files} files written" if files else "",
            f"  🔗 Git repo initialized" if git else "",
            "",
            "Adi ready bro! `ls` cheyyi choodu. Emanna add cheyyala? 🚀",
        ]
        return "\n".join(line for line in lines if line)
    else:
        failed_step = execution_result.get("failed_step", -1)
        error = results[failed_step].get("error", "Unknown error") if results else "Unknown error"
        return (
            f"❌ **Oops bro — Step {failed_step + 1} lo issue vachindi!**\n\n"
            f"  {error}\n\n"
            f"{completed} steps completed, {total - completed} pending.\n"
            f"Fix chesi malli try cheyyi bro! 💪"
        )
