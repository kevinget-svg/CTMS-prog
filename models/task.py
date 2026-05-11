"""Task CRUD operations with rank-filtered queries."""

from database.connection import get_db


def get_categories():
    db = get_db()
    return db.execute("SELECT * FROM task_categories ORDER BY sort_order").fetchall()


def get_subtypes(category_id: int = None):
    db = get_db()
    if category_id:
        return db.execute(
            "SELECT * FROM task_subtypes WHERE category_id = ? ORDER BY sort_order",
            (category_id,),
        ).fetchall()
    return db.execute("""
        SELECT ts.*, tc.name as category_name
        FROM task_subtypes ts
        JOIN task_categories tc ON ts.category_id = tc.id
        ORDER BY tc.sort_order, ts.sort_order
    """).fetchall()


def get_tasks_for_user(user: dict):
    """Get tasks based on user rank."""
    db = get_db()
    rank = user.get("role_rank", 0)
    uid = user["id"]

    base_query = """
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name,
               p.protocol_number, p.study_name,
               ts.name as subtype_name, ts.code as subtype_code,
               tc.name as category_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        LEFT JOIN projects p ON t.project_id = p.id
        LEFT JOIN task_subtypes ts ON t.subtype_id = ts.id
        LEFT JOIN task_categories tc ON ts.category_id = tc.id
    """

    if rank >= 40:
        return db.execute(base_query + " ORDER BY t.updated_at DESC").fetchall()
    elif rank >= 30:
        return db.execute(
            base_query + """
            JOIN project_members pm ON t.project_id = pm.project_id
            WHERE pm.user_id = ?
            ORDER BY t.updated_at DESC
            """, (uid,),
        ).fetchall()
    elif rank >= 20:
        return db.execute(
            base_query + """
            WHERE t.assigned_to = ? OR t.reviewer_id = ?
            ORDER BY t.updated_at DESC
            """, (uid, uid),
        ).fetchall()
    else:
        return db.execute(
            base_query + " WHERE t.assigned_to = ? ORDER BY t.updated_at DESC",
            (uid,),
        ).fetchall()


def get_by_id(task_id: int):
    db = get_db()
    return db.execute("""
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name,
               p.protocol_number, p.study_name,
               ts.name as subtype_name, ts.code as subtype_code,
               tc.name as category_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        LEFT JOIN projects p ON t.project_id = p.id
        LEFT JOIN task_subtypes ts ON t.subtype_id = ts.id
        LEFT JOIN task_categories tc ON ts.category_id = tc.id
        WHERE t.id = ?
    """, (task_id,)).fetchone()


def create(project_id: int, title: str, assigned_to: int, reviewer_id: int = None,
           description: str = "", subtype_id: int = None,
           priority: str = "Normal", due_date: str = None, estimated_hours: float = None):
    db = get_db()
    db.execute("""
        INSERT INTO tasks (project_id, title, assigned_to, reviewer_id, description,
                          subtype_id, priority, due_date, estimated_hours)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (project_id, title, assigned_to, reviewer_id, description, subtype_id, priority, due_date, estimated_hours))
    db.commit()


def update_status(task_id: int, status: str):
    db = get_db()
    db.execute(
        "UPDATE tasks SET status = ?, updated_at = datetime('now','localtime') WHERE id = ?",
        (status, task_id),
    )
    db.commit()


def update_task(task_id: int, **kwargs):
    db = get_db()
    allowed = {"title", "description", "subtype_id", "assigned_to", "reviewer_id",
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
    db = get_db()
    query = """
        SELECT t.*, u.full_name as assignee_name, rv.full_name as reviewer_name,
               ts.name as subtype_name, tc.name as category_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN users rv ON t.reviewer_id = rv.id
        LEFT JOIN task_subtypes ts ON t.subtype_id = ts.id
        LEFT JOIN task_categories tc ON ts.category_id = tc.id
        WHERE t.project_id = ?
    """
    params = [project_id]
    if user:
        rank = user.get("role_rank", 0)
        if rank < 20:
            query += " AND t.assigned_to = ?"
            params.append(user["id"])
        elif rank < 30:
            query += " AND (t.assigned_to = ? OR t.reviewer_id = ?)"
            params.extend([user["id"], user["id"]])
    query += " ORDER BY t.created_at DESC"
    return db.execute(query, params).fetchall()
