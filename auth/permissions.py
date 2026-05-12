"""Permission checks for CTMS STAT — rank-based access control.

Role ranks (higher = more permissions):
    10 = Programmer
    20 = Reviewer
    30 = Manager
    40 = Admin
"""

import streamlit as st
from auth.auth_manager import get_current_user


def get_rank(user: dict) -> int:
    """Get numeric rank from user dict. Default 0 if missing."""
    return user.get("role_rank", 0) if isinstance(user, dict) else 0


def get_role_name(user: dict) -> str:
    """Get role name from user dict."""
    return user.get("role_name", "Unknown") if isinstance(user, dict) else "Unknown"


def can_view_task(user: dict, task: dict) -> bool:
    """Check if user can view a specific task."""
    rank = get_rank(user)
    if rank >= 40:
        return True
    if rank >= 30:
        return True  # Manager sees all in their projects (filtering done in query)
    if rank >= 20:
        return task["assigned_to"] == user["id"] or task["reviewer_id"] == user["id"]
    # Programmer (rank 10)
    return task["assigned_to"] == user["id"]


def can_edit_task(user: dict, task: dict) -> bool:
    """Check if user can edit a task's status/fields."""
    rank = get_rank(user)
    if rank >= 40:
        return True
    if rank >= 30:
        return True
    if rank >= 20:
        return task["reviewer_id"] == user["id"] or task["assigned_to"] == user["id"]
    return task["assigned_to"] == user["id"]


def can_view_timesheet(user: dict, entry_user_id: int) -> bool:
    """Check if user can view timesheet entries for a specific user."""
    rank = get_rank(user)
    if rank >= 30:
        return True
    return user["id"] == entry_user_id


def can_manage_users(user: dict) -> bool:
    """Only Admin (rank >= 40) can manage users and roles."""
    return get_rank(user) >= 40


def can_manage_projects(user: dict) -> bool:
    """Admin and Manager can manage projects."""
    return get_rank(user) >= 30


def can_create_tasks(user: dict) -> bool:
    """Admin and Manager can create tasks."""
    return get_rank(user) >= 30


def is_reviewer(user: dict) -> bool:
    return get_rank(user) >= 20


def is_programmer(user: dict) -> bool:
    return get_rank(user) >= 10


def get_effective_rank(user: dict, project_id: int = None) -> int:
    """Get the user's rank in the given project. Falls back to global rank."""
    if project_id and user and "id" in user:
        from database.connection import get_db
        db = get_db()
        row = db.execute(
            """SELECT r.rank FROM project_members pm
               JOIN roles r ON pm.role_id = r.id
               WHERE pm.project_id = ? AND pm.user_id = ?""",
            (project_id, user["id"]),
        ).fetchone()
        if row:
            return row["rank"]
    return get_rank(user)


def get_effective_role_name(user: dict, project_id: int = None) -> str:
    """Get the user's role name in the given project. Falls back to global."""
    if project_id and user and "id" in user:
        from database.connection import get_db
        db = get_db()
        row = db.execute(
            """SELECT r.name FROM project_members pm
               JOIN roles r ON pm.role_id = r.id
               WHERE pm.project_id = ? AND pm.user_id = ?""",
            (project_id, user["id"]),
        ).fetchone()
        if row:
            return row["name"]
    return get_role_name(user)


def get_visible_ranks(user_rank: int) -> list:
    """Return list of ranks visible to the given user rank."""
    return [r for r in [10, 20, 30, 40] if r <= user_rank]
