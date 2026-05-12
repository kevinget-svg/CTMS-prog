"""Project CRUD operations."""

from database.connection import get_db


def get_all():
    db = get_db()
    return db.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()


def get_by_id(project_id: int):
    db = get_db()
    return db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()


def create(protocol_number: str, study_name: str, sponsor: str = None, description: str = None):
    db = get_db()
    db.execute(
        "INSERT INTO projects (protocol_number, study_name, sponsor, description) VALUES (?,?,?,?)",
        (protocol_number, study_name, sponsor, description),
    )
    db.commit()


def update_status(project_id: int, status: str):
    db = get_db()
    db.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
    db.commit()


def get_members(project_id: int):
    db = get_db()
    return db.execute("""
        SELECT u.*, r.name as role_name, r.rank as role_rank
        FROM users u
        JOIN project_members pm ON u.id = pm.user_id
        JOIN roles r ON pm.role_id = r.id
        WHERE pm.project_id = ? AND u.is_active = 1
        ORDER BY r.rank DESC, u.full_name
    """, (project_id,)).fetchall()


def add_member(project_id: int, user_id: int, role_id: int = None):
    db = get_db()
    if role_id is None:
        u = db.execute("SELECT role_id FROM users WHERE id = ?", (user_id,)).fetchone()
        role_id = u["role_id"] if u else None
    db.execute(
        "INSERT OR IGNORE INTO project_members (project_id, user_id, role_id) VALUES (?,?,?)",
        (project_id, user_id, role_id),
    )
    db.commit()


def remove_member(project_id: int, user_id: int):
    db = get_db()
    db.execute(
        "DELETE FROM project_members WHERE project_id = ? AND user_id = ?",
        (project_id, user_id),
    )
    db.commit()


def get_projects_for_user(user_id: int, is_admin: bool = False):
    db = get_db()
    if is_admin:
        return db.execute("""
            SELECT p.*, NULL as member_role_id
            FROM projects p
            ORDER BY p.created_at DESC
        """).fetchall()
    return db.execute("""
        SELECT p.*, pm.role_id as member_role_id
        FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE pm.user_id = ?
        ORDER BY p.created_at DESC
    """, (user_id,)).fetchall()
