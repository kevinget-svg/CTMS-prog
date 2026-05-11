"""Task CRUD operations with rank-filtered queries."""

from database.connection import get_db


def get_tasks_for_user(user: dict):
    """Get tasks based on user rank."""
    db = get_db()
    rank = user.get("role_rank", 0)
    uid = user["id"]

    base_query = """
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name,
               p.protocol_number, p.study_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        LEFT JOIN projects p ON t.project_id = p.id
    """

    if rank >= 40:  # Admin: all tasks
        return db.execute(base_query + " ORDER BY t.updated_at DESC").fetchall()
    elif rank >= 30:  # Manager: tasks in their projects
        return db.execute(
            base_query + """
            JOIN project_members pm ON t.project_id = pm.project_id
            WHERE pm.user_id = ?
            ORDER BY t.updated_at DESC
            """, (uid,),
        ).fetchall()
    elif rank >= 20:  # Reviewer: own tasks + tasks assigned for review
        return db.execute(
            base_query + """
            WHERE t.assigned_to = ? OR t.reviewer_id = ?
            ORDER BY t.updated_at DESC
            """, (uid, uid),
        ).fetchall()
    else:  # Programmer (rank >= 10): own tasks only
        return db.execute(
            base_query + " WHERE t.assigned_to = ? ORDER BY t.updated_at DESC",
            (uid,),
        ).fetchall()


def get_by_id(task_id: int):
    db = get_db()
    return db.execute("""
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name,
               p.protocol_number, p.study_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.id = ?
    """, (task_id,)).fetchone()


def create(project_id: int, title: str, assigned_to: int, reviewer_id: int = None,
           description: str = "", tfl_type: str = None, priority: str = "Normal",
           due_date: str = None, estimated_hours: float = None):
    db = get_db()
    db.execute("""
        INSERT INTO tasks (project_id, title, assigned_to, reviewer_id, description,
                          tfl_type, priority, due_date, estimated_hours)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (project_id, title, assigned_to, reviewer_id, description, tfl_type, priority, due_date, estimated_hours))
    db.commit()


def update_status(task_id: int, status: str):
    db = get_db()
    db.execute(
        "UPDATE tasks SET status = ?, updated_at = datetime('now','localtime') WHERE id = ?",
        (status, task_id),
    )
    db.commit()


def update_task(task_id: int, **kwargs):
    """Update arbitrary task fields."""
    db = get_db()
    allowed = {"title", "description", "assigned_to", "reviewer_id", "tfl_type",
               "priority", "due_date", "estimated_hours", "status"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = "datetime('now','localtime')"
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]
    db.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    db.commit()


def get_awaiting_qc(reviewer_id: int = None):
    db = get_db()
    if reviewer_id:
        return db.execute("""
            SELECT t.*, u.full_name as assignee_name, p.protocol_number
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status = 'Awaiting QC' AND t.reviewer_id = ?
            ORDER BY t.updated_at DESC
        """, (reviewer_id,)).fetchall()
    return db.execute("""
        SELECT t.*, u.full_name as assignee_name, p.protocol_number
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.status = 'Awaiting QC'
        ORDER BY t.updated_at DESC
    """).fetchall()


def get_by_project(project_id: int, user: dict = None):
    """Get tasks for a project, optionally filtered by user rank."""
    db = get_db()
    query = """
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        WHERE t.project_id = ?
    """
    params = [project_id]
    if user:
        rank = user.get("role_rank", 0)
        if rank < 20:  # Programmer
            query += " AND t.assigned_to = ?"
            params.append(user["id"])
        elif rank < 30:  # Reviewer
            query += " AND (t.assigned_to = ? OR t.reviewer_id = ?)"
            params.extend([user["id"], user["id"]])
        # Manager/Admin sees all in project
    query += " ORDER BY t.created_at DESC"
    return db.execute(query, params).fetchall()
