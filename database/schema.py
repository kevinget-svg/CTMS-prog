"""Database schema initialization for CTMS STAT."""

SCHEMA = """
CREATE TABLE IF NOT EXISTS roles (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    UNIQUE NOT NULL,
    rank    INTEGER NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    UNIQUE NOT NULL,
    password_hash   TEXT    NOT NULL,
    full_name       TEXT    NOT NULL,
    email           TEXT,
    role_id         INTEGER REFERENCES roles(id),
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_number TEXT    UNIQUE NOT NULL,
    study_name      TEXT    NOT NULL,
    sponsor         TEXT,
    status          TEXT    NOT NULL DEFAULT 'Active'
                        CHECK(status IN ('Active','Completed','On Hold')),
    description     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS project_members (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    user_id         INTEGER NOT NULL REFERENCES users(id),
    UNIQUE(project_id, user_id)
);

CREATE TABLE IF NOT EXISTS tfl_shells (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    tfl_number      TEXT    NOT NULL,
    tfl_type        TEXT    NOT NULL CHECK(tfl_type IN ('Table','Figure','Listing')),
    title           TEXT    NOT NULL,
    population      TEXT,
    sap_reference   TEXT,
    status          TEXT    NOT NULL DEFAULT 'Draft'
                        CHECK(status IN ('Draft','Approved','Retired')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE(project_id, tfl_number)
);

CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    shell_id        INTEGER REFERENCES tfl_shells(id),
    assigned_to     INTEGER NOT NULL REFERENCES users(id),
    reviewer_id     INTEGER REFERENCES users(id),
    title           TEXT    NOT NULL,
    description     TEXT,
    tfl_type        TEXT    CHECK(tfl_type IN ('Table','Figure','Listing','Analysis','Other')),
    status          TEXT    NOT NULL DEFAULT 'Not Started'
                        CHECK(status IN (
                            'Not Started','In Progress','Awaiting QC',
                            'QC In Review','Revision Needed','Complete'
                        )),
    priority        TEXT    NOT NULL DEFAULT 'Normal'
                        CHECK(priority IN ('Low','Normal','High','Critical')),
    due_date        TEXT,
    estimated_hours REAL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS timesheet_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    task_id         INTEGER NOT NULL REFERENCES tasks(id),
    work_date       TEXT    NOT NULL,
    hours           REAL    NOT NULL CHECK(hours > 0 AND hours <= 24),
    description     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE(user_id, task_id, work_date)
);

CREATE TABLE IF NOT EXISTS file_versions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         INTEGER NOT NULL REFERENCES tasks(id),
    uploaded_by     INTEGER NOT NULL REFERENCES users(id),
    filename        TEXT    NOT NULL,
    stored_path     TEXT    NOT NULL,
    file_type       TEXT    NOT NULL CHECK(file_type IN (
                        'SAS_Program','R_Script','Output_PDF',
                        'Output_RTF','Output_Excel','Log','Other'
                    )),
    version_number  INTEGER NOT NULL DEFAULT 1,
    file_size_bytes INTEGER,
    comment         TEXT,
    is_double_prog  INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS qc_reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         INTEGER NOT NULL REFERENCES tasks(id),
    reviewer_id     INTEGER NOT NULL REFERENCES users(id),
    status          TEXT    NOT NULL DEFAULT 'Pending'
                        CHECK(status IN ('Pending','Approved','Rejected')),
    comments        TEXT,
    reviewed_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

# Default roles with rank (higher = more permissions)
DEFAULT_ROLES = [
    (10, "Programmer", "Statistical programmer"),
    (20, "Reviewer",    "QC reviewer"),
    (30, "Manager",     "Project/team manager"),
    (40, "Admin",       "System administrator"),
]

# Old role mapping for migration
ROLE_RANK_MAP = {
    "Programmer": 10,
    "Reviewer": 20,
    "Manager": 30,
    "Admin": 40,
}


def init_db(conn):
    """Execute CREATE TABLE IF NOT EXISTS statements. Idempotent."""
    conn.executescript(SCHEMA)
    conn.commit()


def migrate(conn):
    """Run schema migrations for upgrades from older versions."""
    init_db(conn)

    # Ensure roles exist
    existing = conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    if existing == 0:
        for rank, name, desc in DEFAULT_ROLES:
            conn.execute(
                "INSERT INTO roles (rank, name, description) VALUES (?,?,?)",
                (rank, name, desc),
            )
        conn.commit()

    # Upgrade: if users table still has old 'role' text column, migrate to role_id
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = {row["name"] for row in cursor.fetchall()}
    if "role" in columns and "role_id" in columns:
        # Check if any users have role_id = NULL but role is set
        unmigrated = conn.execute(
            "SELECT id, role FROM users WHERE role_id IS NULL AND role IS NOT NULL"
        ).fetchall()
        for u in unmigrated:
            rank = ROLE_RANK_MAP.get(u["role"], 10)
            role_row = conn.execute(
                "SELECT id FROM roles WHERE rank = ?", (rank,)
            ).fetchone()
            if role_row:
                conn.execute(
                    "UPDATE users SET role_id = ? WHERE id = ?",
                    (role_row["id"], u["id"]),
                )
        conn.commit()
