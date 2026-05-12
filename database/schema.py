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

CREATE TABLE IF NOT EXISTS task_categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    UNIQUE NOT NULL,
    sort_order   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS task_subtypes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES task_categories(id),
    name        TEXT    NOT NULL,
    code        TEXT    NOT NULL,
    sort_order   INTEGER NOT NULL DEFAULT 0,
    UNIQUE(category_id, code)
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
    subtype_id      INTEGER REFERENCES task_subtypes(id),
    assigned_to     INTEGER NOT NULL REFERENCES users(id),
    reviewer_id     INTEGER REFERENCES users(id),
    title           TEXT    NOT NULL,
    description     TEXT,
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

DEFAULT_ROLES = [
    (10, "SP",  "编程员：生成aCRF、撰写SDTM/ADaM spec、SAS/R编程生成SDTM/ADaM数据集和TFL、生成define.xml/SDRG/ADRG"),
    (25, "SA",  "统计师：撰写SAP、审阅ADaM spec、审阅TFL结果"),
    (35, "LSP", "编程Leader：布置编程任务、管理项目进度、审阅aCRF/SDTM spec/ADaM spec/define.xml/SDRG/ADRG、审阅TFL shell和结果、数据和文件归档"),
    (40, "Admin", "系统管理员"),
]

ROLE_RANK_MAP = {
    "Programmer": 10,
    "Reviewer": 25,
    "Manager": 35,
    "Admin": 40,
}

# Task categories and subtypes per CDISC SDTMIG 3.4 & ADaMIG 1.3
CATEGORIES = {
    "文档撰写": [
        ("aCRF", "eCRF审阅"),
        ("SDTM Spec", "SDTM数据规格说明"),
        ("ADaM Spec", "ADaM数据规格说明"),
        ("define.xml", "数据集定义文件"),
        ("SDRG", "SDTM审阅者指南"),
        ("ADRG", "ADaM审阅者指南"),
        ("TFL Shell", "TFL模板"),
    ],
    "SDTM": [
        ("DM", "人口学"),
        ("AE", "不良事件"),
        ("CM", "合并用药"),
        ("LB", "实验室检查"),
        ("VS", "生命体征"),
        ("MH", "病史"),
        ("EG", "心电图"),
        ("EX", "暴露"),
        ("EC", "暴露-收集"),
        ("DS", "分布"),
        ("DV", "方案偏离"),
        ("IE", "入排标准"),
        ("SV", "访视"),
        ("SE", "受试者元素"),
        ("QS", "问卷"),
        ("DA", "药物计数"),
        ("MB", "微生物"),
        ("MS", "微生物药敏"),
        ("PC", "药代浓度"),
        ("PP", "药代参数"),
        ("PR", "药效"),
        ("RS", "疾病应答"),
        ("TU", "肿瘤标识"),
        ("TR", "肿瘤结果"),
        ("CO", "评价"),
        ("DD", "死亡详情"),
        ("DI", "设备标识"),
        ("FA", "发现-评估"),
        ("HO", "病史-住院"),
        ("PE", "体格检查"),
        ("RE", "生殖-评估"),
        ("SS", "受试者状态"),
        ("TD", "时间-每日"),
        ("TI", "时间"),
        ("TS", "研究摘要"),
        ("TV", "访视时间点"),
    ],
    "ADaM": [
        ("ADSL", "受试者水平分析数据集"),
        ("ADAE", "不良事件分析数据集"),
        ("ADCM", "合并用药分析数据集"),
        ("ADLB", "实验室检查分析数据集"),
        ("ADVS", "生命体征分析数据集"),
        ("ADMH", "病史分析数据集"),
        ("ADEG", "心电图分析数据集"),
        ("ADEX", "暴露分析数据集"),
        ("ADTTE", "事件时间分析数据集"),
        ("ADQS", "问卷分析数据集"),
        ("ADIS", "免疫原性分析数据集"),
        ("ADRS", "疾病应答分析数据集"),
        ("ADPC", "药代浓度分析数据集"),
        ("ADPP", "药代参数分析数据集"),
    ],
    "TFL": [
        ("T-POP", "人群分布"),
        ("T-BASE", "基线特征"),
        ("T-EFF", "疗效分析"),
        ("T-SAFE", "安全性分析"),
    ],
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

    # Seed task categories and subtypes
    seed_task_types(conn)

    # Upgrade: add subtype_id column to tasks (replaces old tfl_type)
    cursor = conn.execute("PRAGMA table_info(tasks)")
    task_columns = {row["name"] for row in cursor.fetchall()}
    if "subtype_id" not in task_columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN subtype_id INTEGER REFERENCES task_subtypes(id)")
        conn.commit()

    # Upgrade: if users table still has old 'role' text column, migrate to role_id
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = {row["name"] for row in cursor.fetchall()}
    if "role" in columns and "role_id" in columns:
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


def seed_task_types(conn):
    """Insert or update task categories and subtypes (idempotent)."""
    cat_order = {"文档撰写": 1, "SDTM": 2, "ADaM": 3, "TFL": 4}
    for cat_name, subtypes in CATEGORIES.items():
        existing = conn.execute(
            "SELECT id FROM task_categories WHERE name = ?", (cat_name,)
        ).fetchone()
        if existing:
            cat_id = existing["id"]
        else:
            cur = conn.execute(
                "INSERT INTO task_categories (name, sort_order) VALUES (?,?)",
                (cat_name, cat_order.get(cat_name, 99)),
            )
            cat_id = cur.lastrowid

        for idx, (code, name) in enumerate(subtypes):
            sub = conn.execute(
                "SELECT id FROM task_subtypes WHERE category_id = ? AND code = ?",
                (cat_id, code),
            ).fetchone()
            if not sub:
                conn.execute(
                    "INSERT INTO task_subtypes (category_id, name, code, sort_order) VALUES (?,?,?,?)",
                    (cat_id, name, code, idx),
                )
    conn.commit()
