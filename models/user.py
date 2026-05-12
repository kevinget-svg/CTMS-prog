"""User CRUD operations."""

from database.connection import get_db


def get_all(include_inactive: bool = False):
    db = get_db()
    query = """
        SELECT u.*, r.name as role_name, r.rank as role_rank
        FROM users u JOIN roles r ON u.role_id = r.id
    """
    if not include_inactive:
        query += " WHERE u.is_active = 1"
    query += " ORDER BY r.rank DESC, u.full_name"
    return db.execute(query).fetchall()


def get_by_id(user_id: int):
    db = get_db()
    return db.execute(
        """SELECT u.*, r.name as role_name, r.rank as role_rank
           FROM users u JOIN roles r ON u.role_id = r.id
           WHERE u.id = ?""",
        (user_id,),
    ).fetchone()


def get_by_username(username: str):
    db = get_db()
    return db.execute(
        """SELECT u.*, r.name as role_name, r.rank as role_rank
           FROM users u JOIN roles r ON u.role_id = r.id
           WHERE u.username = ?""",
        (username,),
    ).fetchone()


def create(username: str, password_hash: str, full_name: str, role_id: int, email: str = None):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (?,?,?,?,?)",
        (username, password_hash, full_name, email, role_id),
    )
    db.commit()


def update_role(user_id: int, role_id: int):
    db = get_db()
    db.execute("UPDATE users SET role_id = ? WHERE id = ?", (role_id, user_id))
    db.commit()


def deactivate(user_id: int):
    db = get_db()
    db.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    db.commit()


def reactivate(user_id: int):
    db = get_db()
    db.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
    db.commit()


# --- Role Management ---

def get_all_roles():
    db = get_db()
    return db.execute("SELECT * FROM roles ORDER BY rank DESC").fetchall()


def create_role(name: str, rank: int, description: str = None):
    db = get_db()
    db.execute(
        "INSERT INTO roles (name, rank, description) VALUES (?,?,?)",
        (name, rank, description),
    )
    db.commit()


def update_role_info(role_id: int, name: str = None, rank: int = None, description: str = None):
    db = get_db()
    existing = db.execute("SELECT * FROM roles WHERE id = ?", (role_id,)).fetchone()
    if existing is None:
        return
    new_name = name if name is not None else existing["name"]
    new_rank = rank if rank is not None else existing["rank"]
    new_desc = description if description is not None else existing["description"]
    db.execute(
        "UPDATE roles SET name = ?, rank = ?, description = ? WHERE id = ?",
        (new_name, new_rank, new_desc, role_id),
    )
    db.commit()


def delete_role(role_id: int):
    """Delete a role if no users are assigned to it."""
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM users WHERE role_id = ?", (role_id,)).fetchone()[0]
    if count > 0:
        return False, f"Cannot delete: {count} users are assigned to this role."
    db.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    db.commit()
    return True, "Role deleted."
