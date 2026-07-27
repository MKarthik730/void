# -*- coding: utf-8 -*-
"""
VOID Backend — File Management + Project Scaffold Routes
Routes: /files/plan, /files/execute, /files/list, /files/trash
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.project_scaffold_service import plan_project, execute_plan, format_plan_for_response, format_execution_results
from services.file_service import (
    create_file,
    write_file,
    delete_file,
    move_file,
    list_files,
    create_directory,
    is_destructive,
    restore_from_trash,
    FileActionError,
)

router = APIRouter(prefix="/files", tags=["File Management"])


# ── Request Models ────────────────────────────────────────────────────────────

class PlanRequest(BaseModel):
    description: str


class ExecuteRequest(BaseModel):
    plan: List[Dict[str, Any]]


class FileCreateRequest(BaseModel):
    path: str
    content: str = ""


class FileWriteRequest(BaseModel):
    path: str
    content: str
    mode: str = "overwrite"  # "overwrite" or "append"


class FileDeleteRequest(BaseModel):
    path: str


class FileMoveRequest(BaseModel):
    source: str
    destination: str


class FileListRequest(BaseModel):
    path: str = "."
    pattern: str = "*"


class DirectoryCreateRequest(BaseModel):
    path: str


class TrashRestoreRequest(BaseModel):
    filename: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/plan")
def plan_endpoint(request: PlanRequest):
    """Generate a project scaffolding plan without executing (dry run).

    Returns the plan with requires_confirmation flag so the frontend
    can show a confirm dialog before hitting /files/execute.

    Pure creates in new paths never require confirmation.
    """
    try:
        plan = plan_project(request.description)
        destructive = is_destructive(plan)

        return {
            "plan": plan,
            "requires_confirmation": destructive,
            "description": request.description,
            "step_count": len(plan),
            "formatted": format_plan_for_response(plan),
        }
    except FileActionError as e:
        return {"error": str(e), "plan": None, "requires_confirmation": False}
    except Exception as e:
        return {"error": f"Plan generation failed bro: {str(e)[:200]}", "plan": None, "requires_confirmation": False}


@router.post("/execute")
def execute_endpoint(request: ExecuteRequest):
    """Execute a previously returned plan.

    The plan should come from a previous /files/plan response.
    The frontend should show a confirm dialog if requires_confirmation was true.
    """
    plan = request.plan
    if not plan:
        return {"error": "Plan empty bro — first call /files/plan", "results": [], "all_success": False}

    try:
        result = execute_plan(plan)
        return result
    except FileActionError as e:
        return {"error": str(e), "results": [e.to_dict()], "all_success": False}
    except Exception as e:
        return {"error": f"Execution failed bro: {str(e)[:200]}", "results": [], "all_success": False}


@router.post("/create-file")
def create_file_endpoint(request: FileCreateRequest):
    """Create a new file. Never requires confirmation."""
    try:
        result = create_file(request.path, request.content)
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "create_file", "path": request.path, "success": False, "error": str(e)[:200]}


@router.post("/write-file")
def write_file_endpoint(request: FileWriteRequest):
    """Write content to a file. Overwrite mode on existing file requires confirmation."""
    from services.file_service import _resolve_path
    # Check if file exists BEFORE writing
    try:
        target = _resolve_path(request.path)
        existed_before = request.mode == "overwrite" and target.exists()
    except Exception:
        existed_before = False

    try:
        result = write_file(request.path, request.content, request.mode)
        result["requires_confirmation"] = existed_before
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "write_file", "path": request.path, "success": False, "error": str(e)[:200]}


@router.post("/delete-file")
def delete_file_endpoint(request: FileDeleteRequest):
    """Soft-delete a file. Requires confirmation."""
    try:
        result = delete_file(request.path)
        result["requires_confirmation"] = True
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "delete_file", "path": request.path, "success": False, "error": str(e)[:200]}


@router.post("/move-file")
def move_file_endpoint(request: FileMoveRequest):
    """Move or rename a file. Requires confirmation if destination exists."""
    try:
        result = move_file(request.source, request.destination)
        result["requires_confirmation"] = result.get("overwrote", False)
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "move_file", "path": request.source, "success": False, "error": str(e)[:200]}


@router.post("/list")
def list_files_endpoint(request: FileListRequest):
    """List files and directories in a workspace path."""
    try:
        entries = list_files(request.path, request.pattern)
        return {"entries": entries, "count": len(entries)}
    except FileActionError as e:
        return {"entries": [], "count": 0, "error": str(e)}
    except Exception as e:
        return {"entries": [], "count": 0, "error": str(e)[:200]}


@router.post("/mkdir")
def create_directory_endpoint(request: DirectoryCreateRequest):
    """Create a directory. Never requires confirmation."""
    try:
        result = create_directory(request.path)
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "create_directory", "path": request.path, "success": False, "error": str(e)[:200]}


@router.post("/restore-from-trash")
def restore_trash_endpoint(request: TrashRestoreRequest):
    """Restore a file from .void_trash."""
    try:
        result = restore_from_trash(request.filename)
        return result
    except FileActionError as e:
        return e.to_dict()
    except Exception as e:
        return {"action": "restore_from_trash", "path": request.filename, "success": False, "error": str(e)[:200]}
