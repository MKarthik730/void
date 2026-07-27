# -*- coding: utf-8 -*-
"""
VOID — File Management Service
Sandboxed file operations with path traversal protection, soft-delete, and structured results.
All paths are resolved against allowed workspace roots only.
"""

import os
import shutil
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import config


class FileActionError(Exception):
    """Custom exception for file operation failures — never lets raw OSError escape."""
    def __init__(self, message: str, action: str = "", path: str = ""):
        self.action = action
        self.path = path
        self.message = message
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "path": self.path,
            "error": self.message,
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }


# ── Workspace Resolution ──────────────────────────────────────────────────────

def _get_workspace_roots() -> List[Path]:
    """Parse FILE_WORKSPACE_ROOTS env var into a list of absolute Paths."""
    raw = config.FILE_WORKSPACE_ROOTS
    roots = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        # Expand ~ and env vars
        expanded = os.path.expandvars(os.path.expanduser(part))
        p = Path(expanded).resolve()
        roots.append(p)
    # Default fallback
    if not roots:
        roots = [Path.home() / "VOID_Projects"]
    return roots


WORKSPACE_ROOTS = _get_workspace_roots()
TRASH_DIR = WORKSPACE_ROOTS[0] / ".void_trash"


def _resolve_path(user_path: str) -> Path:
    """Resolve a user-provided path to an absolute path within workspace roots.

    Raises FileActionError on:
    - Path traversal (e.g. ../../etc/passwd)
    - Path outside any workspace root
    """
    if not user_path or not user_path.strip():
        raise FileActionError("Path empty ivvaledhu bro", action="resolve", path=user_path)

    # Resolve relative to first workspace root
    path = (WORKSPACE_ROOTS[0] / user_path).resolve()

    # Security: reject if path doesn't start with any allowed root
    # (handles both direct traversal and symlink-based bypass)
    try:
        resolved = path.resolve()
    except (RuntimeError, FileNotFoundError):
        # path might not exist yet; use the logical path
        resolved = path

    allowed = False
    for root in WORKSPACE_ROOTS:
        try:
            resolved.relative_to(root)
            allowed = True
            break
        except ValueError:
            continue

    if not allowed:
        safe_roots = ", ".join(str(r) for r in WORKSPACE_ROOTS)
        raise FileActionError(
            f"Path {user_path} is outside workspace bro. Allowed roots: {safe_roots}",
            action="resolve",
            path=str(path),
        )

    return resolved


def _ensure_trash():
    """Ensure the .void_trash directory exists."""
    TRASH_DIR.mkdir(parents=True, exist_ok=True)


def _result(action: str, path: str, success: bool, extra: Optional[dict] = None) -> dict:
    """Build a structured result dict."""
    result = {
        "action": action,
        "path": path,
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }
    if extra:
        result.update(extra)
    return result


# ── Core File Operations ──────────────────────────────────────────────────────

def create_file(file_path: str, content: str = "") -> dict:
    """Create a new file with optional content. Never requires confirmation.

    Args:
        file_path: Path relative to workspace root, or absolute within workspace
        content: File content (empty string for blank file)

    Returns:
        Structured result dict
    """
    try:
        resolved = _resolve_path(file_path)
        if resolved.exists():
            raise FileActionError(
                f"File already undi bro: {file_path}",
                action="create_file",
                path=str(resolved),
            )

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

        from services.memory_service import log_action
        log_action("file_create", file_path, f"Created {len(content)} bytes")

        return _result("create_file", str(resolved), True, {"size": len(content)})
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="create_file", path=file_path)


def write_file(file_path: str, content: str, mode: str = "overwrite") -> dict:
    """Write content to a file. Overwrite mode requires confirmation.

    Args:
        file_path: Path relative to workspace root
        content: Content to write
        mode: "overwrite" (replace existing) or "append" (add to end)

    Returns:
        Structured result dict
    """
    try:
        resolved = _resolve_path(file_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)

        if mode == "append":
            with open(resolved, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            resolved.write_text(content, encoding="utf-8")

        from services.memory_service import log_action
        log_action("file_write", f"{file_path} ({mode})", f"Wrote {len(content)} bytes")

        return _result("write_file", str(resolved), True, {"mode": mode, "size": len(content)})
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="write_file", path=file_path)


def delete_file(file_path: str) -> dict:
    """Soft-delete a file by moving it to .void_trash. Requires confirmation.

    Args:
        file_path: Path relative to workspace root

    Returns:
        Structured result dict
    """
    try:
        resolved = _resolve_path(file_path)
        if not resolved.exists():
            raise FileActionError(
                f"File dorakaledhu bro: {file_path}",
                action="delete_file",
                path=str(resolved),
            )
        if not resolved.is_file():
            raise FileActionError(
                f"Adi file kaadhu bro: {file_path}",
                action="delete_file",
                path=str(resolved),
            )

        _ensure_trash()
        trash_path = TRASH_DIR / f"{resolved.name}.{int(time.time())}"
        shutil.move(str(resolved), str(trash_path))

        from services.memory_service import log_action
        log_action("file_delete", file_path, f"Moved to trash: {trash_path.name}")

        return _result("delete_file", str(resolved), True, {"trash_path": str(trash_path)})
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="delete_file", path=file_path)


def move_file(source_path: str, dest_path: str) -> dict:
    """Move or rename a file. Requires confirmation if destination exists.

    Args:
        source_path: Current path relative to workspace root
        dest_path: New path relative to workspace root

    Returns:
        Structured result dict with 'overwrote' flag if destination was replaced
    """
    try:
        resolved_src = _resolve_path(source_path)
        resolved_dst = _resolve_path(dest_path)

        if not resolved_src.exists():
            raise FileActionError(
                f"Source file dorakaledhu bro: {source_path}",
                action="move_file",
                path=str(resolved_src),
            )

        overwrote = resolved_dst.exists()
        resolved_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(resolved_src), str(resolved_dst))

        from services.memory_service import log_action
        log_action("file_move", f"{source_path} -> {dest_path}", f"Overwrote: {overwrote}")

        return _result("move_file", str(resolved_dst), True, {"overwrote": overwrote})
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="move_file", path=source_path)


def list_files(directory_path: str = ".", pattern: str = "*") -> List[dict]:
    """List files and directories within a workspace path.

    Args:
        directory_path: Path relative to workspace root
        pattern: Glob pattern for filtering (e.g. "*.py", "**/*")

    Returns:
        List of file info dicts
    """
    try:
        resolved = _resolve_path(directory_path)
        if not resolved.exists():
            raise FileActionError(
                f"Directory dorakaledhu bro: {directory_path}",
                action="list_files",
                path=str(resolved),
            )
        if not resolved.is_dir():
            raise FileActionError(
                f"Adi directory kaadhu bro: {directory_path}",
                action="list_files",
                path=str(resolved),
            )

        entries = []
        for entry in resolved.glob(pattern):
            if entry.name.startswith(".") and entry.name != ".":
                continue
            try:
                stat = entry.stat()
                entries.append({
                    "name": entry.name,
                    "path": str(entry.relative_to(WORKSPACE_ROOTS[0])),
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            except OSError:
                continue

        return entries
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="list_files", path=directory_path)


def create_directory(dir_path: str) -> dict:
    """Create a directory (and any parent directories). Never requires confirmation.

    Args:
        dir_path: Path relative to workspace root

    Returns:
        Structured result dict
    """
    try:
        resolved = _resolve_path(dir_path)
        resolved.mkdir(parents=True, exist_ok=True)

        from services.memory_service import log_action
        log_action("file_mkdir", dir_path, "Directory created")

        return _result("create_directory", str(resolved), True)
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="create_directory", path=dir_path)


def create_project_structure(files: List[Dict[str, Any]]) -> List[dict]:
    """Create multiple files/directories in one call.

    Args:
        files: List of dicts with keys: type (mkdir|create_file), path, content (optional)

    Returns:
        List of structured result dicts for each step
    """
    results = []
    for step in files:
        step_type = step.get("type", "create_file")
        step_path = step.get("path", "")
        step_content = step.get("content", "")

        try:
            if step_type == "mkdir":
                results.append(create_directory(step_path))
            elif step_type == "create_file":
                results.append(create_file(step_path, step_content or ""))
            else:
                results.append(_result("unknown", step_path, False, {"error": f"Unknown type: {step_type}"}))
        except FileActionError as e:
            results.append(e.to_dict())
            break  # Stop on first failure

    return results


def is_destructive(plan: List[Dict[str, Any]]) -> bool:
    """Check if a plan contains any destructive operations (delete, overwrite, move).

    A step is destructive if:
    - type is 'delete_file' or 'move_file'
    - type is 'write_file' with mode='overwrite' AND the target already exists
    - type is 'create_file' or 'mkdir' AND the target path already exists
    """
    for step in plan:
        step_type = step.get("type", "")
        if step_type in ("delete_file", "move_file"):
            return True

        step_path = step.get("path", "")
        if not step_path:
            continue

        try:
            resolved = _resolve_path(step_path)
            if not resolved.exists():
                continue

            # Existing path + destructive step type = confirmation needed
            if step_type == "write_file" and step.get("mode", "overwrite") == "overwrite":
                return True
            if step_type in ("create_file", "mkdir"):
                return True
        except FileActionError:
            pass  # Path doesn't exist or is invalid — not destructive

    return False


def restore_from_trash(trash_filename: str) -> dict:
    """Restore a file from .void_trash back to its original location.

    Args:
        trash_filename: Name of the file in .void_trash (includes timestamp suffix)

    Returns:
        Structured result dict
    """
    try:
        _ensure_trash()
        trash_path = TRASH_DIR / trash_filename
        if not trash_path.exists():
            raise FileActionError(
                f"Trash lo file dorakaledhu: {trash_filename}",
                action="restore_from_trash",
                path=str(trash_path),
            )

        # Derive original name by stripping timestamp suffix
        # Format: {original_name}.{timestamp}
        parts = trash_filename.rsplit(".", 2)
        original_name = parts[0] if len(parts) >= 2 else trash_filename

        # Restore to the first workspace root
        restore_path = WORKSPACE_ROOTS[0] / original_name
        restore_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(trash_path), str(restore_path))

        from services.memory_service import log_action
        log_action("file_restore", trash_filename, f"Restored to {restore_path}")

        return _result("restore_from_trash", str(restore_path), True)
    except FileActionError:
        raise
    except Exception as e:
        raise FileActionError(str(e)[:200], action="restore_from_trash", path=trash_filename)
