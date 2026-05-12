"""Timesheet CRUD operations."""

from database.connection import get_db


def get_by_user_date_range(user_id: int, start_date: str, end_date: str):
    db = get_db()
    return db.execute("""
        SELECT te.*, t.title as task_title, p.protocol_number, p.study_name
        FROM timesheet_entries te
        JOIN tasks t ON te.task_id = t.id
        JOIN projects p ON t.project_id = p.id
        WHERE te.user_id = ? AND te.work_date BETWEEN ? AND ?
        ORDER BY te.work_date DESC, te.created_at DESC
    """, (user_id, start_date, end_date)).fetchall()


def get_weekly_hours(user_id: int, week_start: str, week_end: str):
    db = get_db()
    rows = db.execute("""
        SELECT work_date, SUM(hours) as total_hours
        FROM timesheet_entries
        WHERE user_id = ? AND work_date BETWEEN ? AND ?
        GROUP BY work_date
        ORDER BY work_date
    """, (user_id, week_start, week_end)).fetchall()
    return {row["work_date"]: row["total_hours"] for row in rows}


def get_monthly_aggregation(user_id: int, year: int, month: int):
    db = get_db()
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    rows = db.execute("""
        SELECT te.work_date, te.hours, t.title as task_title, p.protocol_number
        FROM timesheet_entries te
        JOIN tasks t ON te.task_id = t.id
        JOIN projects p ON t.project_id = p.id
        WHERE te.user_id = ? AND te.work_date >= ? AND te.work_date < ?
        ORDER BY te.work_date DESC
    """, (user_id, start, end)).fetchall()
    return rows


def upsert_entry(user_id: int, task_id: int, work_date: str, hours: float, description: str = ""):
    """Insert or update a timesheet entry (one entry per user/task/day)."""
    db = get_db()
    existing = db.execute(
        "SELECT id FROM timesheet_entries WHERE user_id = ? AND task_id = ? AND work_date = ?",
        (user_id, task_id, work_date),
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE timesheet_entries SET hours = ?, description = ? WHERE id = ?",
            (hours, description, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO timesheet_entries (user_id, task_id, work_date, hours, description) VALUES (?,?,?,?,?)",
            (user_id, task_id, work_date, hours, description),
        )
    db.commit()


def get_all_entries(date_from: str = None, date_to: str = None, project_id: int = None):
    """Get all timesheet entries (for Manager/Admin views)."""
    db = get_db()
    query = """
        SELECT te.*, u.full_name as user_name, r.name as role_name, t.title as task_title,
               p.protocol_number, p.study_name
        FROM timesheet_entries te
        JOIN users u ON te.user_id = u.id
        JOIN roles r ON u.role_id = r.id
        JOIN tasks t ON te.task_id = t.id
        JOIN projects p ON t.project_id = p.id
        WHERE 1=1
    """
    params = []
    if date_from:
        query += " AND te.work_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND te.work_date <= ?"
        params.append(date_to)
    if project_id:
        query += " AND p.id = ?"
        params.append(project_id)
    query += " ORDER BY te.work_date DESC, u.full_name"
    return db.execute(query, params).fetchall()


def get_project_hours(project_id: int, date_from: str = None, date_to: str = None):
    """Get aggregated hours per user for a project."""
    db = get_db()
    query = """
        SELECT u.id, u.full_name, r.name as role_name, SUM(te.hours) as total_hours, COUNT(DISTINCT te.work_date) as days_worked
        FROM timesheet_entries te
        JOIN users u ON te.user_id = u.id
        JOIN roles r ON u.role_id = r.id
        JOIN tasks t ON te.task_id = t.id
        WHERE t.project_id = ?
    """
    params = [project_id]
    if date_from:
        query += " AND te.work_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND te.work_date <= ?"
        params.append(date_to)
    query += " GROUP BY u.id ORDER BY total_hours DESC"
    return db.execute(query, params).fetchall()
