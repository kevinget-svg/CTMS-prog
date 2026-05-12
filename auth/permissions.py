"""Permission checks for CTMS STAT — rank-based access control.

Role ranks (higher = more permissions):
    10 = SP / 25 = SA / 35 = LSP / 40 = Admin
"""

from auth.auth_manager import get_current_user


def get_rank(user: dict) -> int:
    """Get numeric rank from user dict. Default 0 if missing."""
    return user.get("role_rank", 0) if isinstance(user, dict) else 0


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


def can_manage_projects(user: dict) -> bool:
    """Admin and Manager can manage projects."""
    return get_rank(user) >= 30


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
    return user.get("role_name", "Unknown") if isinstance(user, dict) else "Unknown"
