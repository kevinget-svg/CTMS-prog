"""Seed the database with initial admin user and demo data."""

import bcrypt
from database.schema import init_db, migrate


def seed(conn):
    """Create seed data if users table is empty."""
    init_db(conn)
    migrate(conn)

    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        return

    # Get role IDs
    roles = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM roles").fetchall()}

    def add_user(username, password, full_name, email, role_name):
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (?,?,?,?,?)",
            (username, pw_hash, full_name, email, roles[role_name]),
        )

    add_user("admin", "admin123", "System Admin", "admin@example.com", "Admin")
    add_user("manager", "manager123", "Zhang Wei", "zhangwei@example.com", "Manager")
    add_user("programmer1", "dev123", "Li Ming", "liming@example.com", "Programmer")
    add_user("reviewer1", "reviewer123", "Wang Fang", "wangfang@example.com", "Reviewer")

    # Create demo project
    conn.execute(
        "INSERT INTO projects (protocol_number, study_name, sponsor, status, description) VALUES (?,?,?,?,?)",
        ("ABC-123-001", "Phase III Study in Psoriasis", "ABC Pharma", "Active",
         "A randomized, double-blind, placebo-controlled study"),
    )

    # Get user IDs
    users = {u["username"]: u["id"] for u in conn.execute("SELECT id, username FROM users").fetchall()}

    # Add all users to project
    for uid in users.values():
        conn.execute("INSERT INTO project_members (project_id, user_id) VALUES (1, ?)", (uid,))

    # Demo TFL shells
    shells = [
        ("T14.1.1", "Table", "Demographics and Baseline Characteristics", "ITT"),
        ("T14.1.2", "Table", "Primary Endpoint Analysis", "ITT"),
        ("T14.2.1", "Table", "Adverse Events Summary", "Safety"),
        ("T14.2.2", "Table", "Laboratory Parameters", "Safety"),
        ("F1.1", "Figure", "Kaplan-Meier Plot of Time to Event", "ITT"),
        ("L16.2.1", "Listing", "Patient Disposition Listing", "ITT"),
    ]
    for tfl_num, tfl_type, title, pop in shells:
        status = "Approved" if tfl_type != "Listing" else "Draft"
        conn.execute(
            "INSERT INTO tfl_shells (project_id, tfl_number, tfl_type, title, population, status) VALUES (?,?,?,?,?,?)",
            (1, tfl_num, tfl_type, title, pop, status),
        )

    # Demo tasks
    pid = users["programmer1"]
    rid = users["reviewer1"]
    tasks = [
        (1, pid, rid, "Create Demographics Table", "Generate T14.1.1 output from SDTM", "Table", "In Progress", "High", "2026-05-15", 8.0),
        (1, pid, rid, "Create Primary Endpoint Table", "Generate T14.1.2 output", "Table", "Not Started", "High", "2026-05-20", 12.0),
        (1, pid, rid, "Create AE Summary Table", "Generate T14.2.1 output", "Table", "Not Started", "Normal", "2026-05-25", 16.0),
        (1, pid, None, "SDTM Mapping Review", "Review SDTM mappings for all domains", "Other", "Complete", "Normal", "2026-05-05", 4.0),
    ]
    for proj_id, assignee, reviewer, title, desc, tfl_type, status, priority, due, est in tasks:
        conn.execute(
            "INSERT INTO tasks (project_id, assigned_to, reviewer_id, title, description, tfl_type, status, priority, due_date, estimated_hours) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (proj_id, assignee, reviewer, title, desc, tfl_type, status, priority, due, est),
        )

    # Demo timesheet entries
    task_rows = conn.execute("SELECT id FROM tasks").fetchall()
    t1, t2, t3, t4 = [t["id"] for t in task_rows]
    entries = [
        (pid, t1, "2026-05-06", 4.0, "Wrote SAS program for demographics table"),
        (pid, t1, "2026-05-07", 3.0, "Debugged output formatting"),
        (pid, t2, "2026-05-06", 2.0, "Reviewed SAP section 14.1"),
        (pid, t4, "2026-05-03", 3.5, "SDTM domain review: DM, AE, LB"),
        (pid, t4, "2026-05-04", 2.5, "Completed SDTM mapping review"),
    ]
    for uid, tid, date, hours, desc in entries:
        conn.execute(
            "INSERT INTO timesheet_entries (user_id, task_id, work_date, hours, description) VALUES (?,?,?,?,?)",
            (uid, tid, date, hours, desc),
        )

    conn.commit()
    print("Seed data created successfully.")
    print("  Admin:      admin / admin123")
    print("  Manager:    manager / manager123")
    print("  Programmer: programmer1 / dev123")
    print("  Reviewer:   reviewer1 / reviewer123")
