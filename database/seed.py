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

    add_user("admin", "admin123", "Admin", "admin@example.com", "Admin")
    add_user("lsp_wang", "lsp123", "Wang Qiang", "wangqiang@example.com", "LSP")
    add_user("sa_zhang", "sa123", "Zhang Li", "zhangli@example.com", "SA")
    add_user("sp_li", "sp123", "Li Ming", "liming@example.com", "SP")

    # Get subtype IDs
    subtypes = {}
    for row in conn.execute("""
        SELECT ts.id, ts.code, tc.name as cat
        FROM task_subtypes ts JOIN task_categories tc ON ts.category_id = tc.id
    """).fetchall():
        subtypes[row["code"]] = row["id"]

    def st(code):
        return subtypes.get(code)

    # Demo projects
    conn.execute(
        "INSERT INTO projects (protocol_number, study_name, sponsor, status, description) VALUES (?,?,?,?,?)",
        ("ABC-123-001", "一项评估XXX治疗银屑病的III期随机双盲安慰剂对照研究", "ABC制药", "Active",
         "Phase III, randomized, double-blind, placebo-controlled, multicenter study"),
    )
    conn.execute(
        "INSERT INTO projects (protocol_number, study_name, sponsor, status, description) VALUES (?,?,?,?,?)",
        ("DEF-456-002", "XXX治疗2型糖尿病的II期剂量探索研究", "DEF生物", "Active",
         "Phase II, dose-finding study in type 2 diabetes"),
    )

    users = {u["username"]: u["id"] for u in conn.execute("SELECT id, username FROM users").fetchall()}

    for uid in users.values():
        conn.execute("INSERT INTO project_members (project_id, user_id) VALUES (1, ?)", (uid,))
    conn.execute("INSERT INTO project_members (project_id, user_id) VALUES (2, ?)", (users["lsp_wang"],))
    conn.execute("INSERT INTO project_members (project_id, user_id) VALUES (2, ?)", (users["sp_li"],))
    conn.execute("INSERT INTO project_members (project_id, user_id) VALUES (2, ?)", (users["sa_zhang"],))

    sp_uid = users["sp_li"]
    sa_uid = users["sa_zhang"]
    lsp_uid = users["lsp_wang"]

    # TFL shells — project 1
    shells = [
        ("T14.1.1", "Table", "人口学与基线特征", "ITT"),
        ("T14.1.2", "Table", "主要终点分析", "ITT"),
        ("T14.1.3", "Table", "次要终点分析", "ITT"),
        ("T14.2.1", "Table", "不良事件总结", "Safety"),
        ("T14.2.2", "Table", "实验室检查变化", "Safety"),
        ("F1.1", "Figure", "主要终点森林图", "ITT"),
        ("L16.2.1", "Listing", "受试者分布列表", "All Subjects"),
        ("L16.2.2", "Listing", "严重不良事件列表", "Safety"),
    ]
    for tfl_num, tfl_type, title, pop in shells:
        conn.execute(
            "INSERT INTO tfl_shells (project_id, tfl_number, tfl_type, title, population, status) VALUES (?,?,?,?,?,?)",
            (1, tfl_num, tfl_type, title, pop, "Approved"),
        )

    # Tasks — Project 1
    tasks_p1 = [
        # SDTM programming
        (1, sp_uid, lsp_uid, "编写DM域SDTM编程", "从EDC人口学数据生成SDTM DM数据集", st("DM"), "Not Started", "High", "2026-05-15", 8.0),
        (1, sp_uid, lsp_uid, "编写AE域SDTM编程", "从EDC不良事件数据生成SDTM AE数据集", st("AE"), "Not Started", "High", "2026-05-15", 8.0),
        (1, sp_uid, lsp_uid, "编写CM域SDTM编程", "从EDC合并用药数据生成SDTM CM数据集", st("CM"), "Not Started", "Normal", "2026-05-18", 6.0),
        (1, sp_uid, lsp_uid, "编写LB域SDTM编程", "从EDC实验室检查数据生成SDTM LB数据集", st("LB"), "In Progress", "High", "2026-05-18", 10.0),
        (1, sp_uid, lsp_uid, "编写VS域SDTM编程", "从EDC生命体征数据生成SDTM VS数据集", st("VS"), "Not Started", "Normal", "2026-05-20", 4.0),
        (1, sp_uid, lsp_uid, "编写MH域SDTM编程", "从EDC病史数据生成SDTM MH数据集", st("MH"), "Not Started", "Normal", "2026-05-20", 4.0),
        # ADaM programming
        (1, sp_uid, sa_uid, "生成ADSL数据集", "从SDTM DM生成受试者水平分析数据集", st("ADSL"), "Not Started", "High", "2026-05-20", 8.0),
        (1, sp_uid, sa_uid, "生成ADAE数据集", "从SDTM AE生成不良事件分析数据集", st("ADAE"), "Not Started", "High", "2026-05-25", 12.0),
        (1, sp_uid, sa_uid, "生成ADLB数据集", "从SDTM LB生成实验室检查分析数据集", st("ADLB"), "Not Started", "Normal", "2026-05-25", 10.0),
        (1, sp_uid, sa_uid, "生成ADTTE数据集", "生存分析，PFS事件时间数据集", st("ADTTE"), "Not Started", "Critical", "2026-05-30", 12.0),
        # TFL
        (1, sp_uid, sa_uid, "T14.1.1 人口学与基线特征表", "ITT人群的人口学与基线特征汇总", st("T-BASE"), "In Progress", "High", "2026-06-01", 8.0),
        (1, sp_uid, sa_uid, "T14.1.2 主要终点分析表", "主要终点第16周MMRM分析", st("T-EFF"), "Not Started", "Critical", "2026-06-05", 12.0),
        (1, sp_uid, sa_uid, "T14.2.1 不良事件总结表", "按SOC/PT汇总TEAE", st("T-SAFE"), "Not Started", "High", "2026-06-10", 16.0),
        (1, sp_uid, sa_uid, "T14.2.2 实验室检查变化表", "实验室指标较基线变化", st("T-SAFE"), "Not Started", "Normal", "2026-06-10", 12.0),
        # Documentation
        (1, sp_uid, lsp_uid, "撰写SDTM Spec", "编写所有SDTM域的数据规格说明", st("SDTM Spec"), "Complete", "High", "2026-04-20", 20.0),
        (1, sp_uid, lsp_uid, "撰写ADaM Spec", "编写所有ADaM数据集规格说明", st("ADaM Spec"), "In Progress", "High", "2026-05-10", 16.0),
        (1, lsp_uid, None, "审阅aCRF", "逐字段审阅eCRF与SDTM/ADaM需求对应", st("aCRF"), "Complete", "High", "2026-04-10", 4.0),
        (1, sa_uid, None, "撰写SAP", "撰写统计分析计划", st("aCRF"), "Complete", "High", "2026-04-05", 16.0),
        (1, sp_uid, lsp_uid, "生成define.xml", "基于SDTM/ADaM元数据生成define.xml", st("define.xml"), "Not Started", "Normal", "2026-06-15", 8.0),
        (1, sp_uid, lsp_uid, "撰写SDRG", "SDTM审阅者指南", st("SDRG"), "Not Started", "Normal", "2026-06-15", 4.0),
        (1, sp_uid, lsp_uid, "撰写ADRG", "ADaM审阅者指南", st("ADRG"), "Not Started", "Normal", "2026-06-20", 4.0),
    ]
    for proj_id, assignee, reviewer, title, desc, subtype_id, status, priority, due, est in tasks_p1:
        conn.execute(
            "INSERT INTO tasks (project_id, assigned_to, reviewer_id, title, description, subtype_id, status, priority, due_date, estimated_hours) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (proj_id, assignee, reviewer, title, desc, subtype_id, status, priority, due, est),
        )

    # Tasks — Project 2
    tasks_p2 = [
        (2, sp_uid, sa_uid, "编写DM域SDTM编程", "PD研究的人口学数据", st("DM"), "Not Started", "Normal", "2026-06-15", 6.0),
        (2, sp_uid, sa_uid, "编写AE域SDTM编程", "PD研究的不良事件数据", st("AE"), "Not Started", "Normal", "2026-06-20", 6.0),
        (2, sp_uid, sa_uid, "生成ADSL数据集", "PD研究受试者水平分析数据集", st("ADSL"), "Not Started", "Normal", "2026-06-25", 8.0),
        (2, sp_uid, sa_uid, "T14.1.1 人口学与基线特征表", "PD研究基线汇总", st("T-BASE"), "Not Started", "Normal", "2026-07-01", 8.0),
    ]
    for proj_id, assignee, reviewer, title, desc, subtype_id, status, priority, due, est in tasks_p2:
        conn.execute(
            "INSERT INTO tasks (project_id, assigned_to, reviewer_id, title, description, subtype_id, status, priority, due_date, estimated_hours) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (proj_id, assignee, reviewer, title, desc, subtype_id, status, priority, due, est),
        )

    # Demo timesheet entries
    task_rows = conn.execute("SELECT id, title FROM tasks WHERE project_id = 1").fetchall()
    task_map = {t["title"]: t["id"] for t in task_rows}

    entries = [
        (sp_uid, task_map["编写LB域SDTM编程"], "2026-05-08", 4.0, "编写LB域SAS程序，处理单位转换"),
        (sp_uid, task_map["编写LB域SDTM编程"], "2026-05-09", 3.0, "LB域QC，验证与原始数据的一致性"),
        (sp_uid, task_map["T14.1.1 人口学与基线特征表"], "2026-05-06", 4.0, "编写人口学汇总SAS程序"),
        (sp_uid, task_map["T14.1.1 人口学与基线特征表"], "2026-05-07", 3.0, "调试RTF输出格式"),
        (sp_uid, task_map["撰写SDTM Spec"], "2026-04-15", 6.0, "编写DM、AE、LB域的mapping"),
        (sp_uid, task_map["撰写SDTM Spec"], "2026-04-16", 5.0, "编写CM、MH、VS域的mapping"),
        (sp_uid, task_map["撰写SDTM Spec"], "2026-04-17", 5.0, "完成初稿，提交LSP审阅"),
        (sp_uid, task_map["撰写ADaM Spec"], "2026-05-08", 4.0, "编写ADSL、ADAE规格说明"),
        (sa_uid, task_map["撰写SAP"], "2026-04-01", 4.0, "起草SAP初稿，确定分析人群与方法"),
        (sa_uid, task_map["撰写SAP"], "2026-04-02", 4.0, "完成主要/次要终点分析方法描述"),
        (sa_uid, task_map["撰写SAP"], "2026-04-03", 4.0, "SAP定稿并提交"),
        (lsp_uid, task_map["审阅aCRF"], "2026-04-08", 3.0, "整体审阅aCRF设计"),
        (lsp_uid, task_map["审阅aCRF"], "2026-04-09", 1.0, "与DM团队沟通修改意见"),
    ]
    for uid, tid, date, hours, desc in entries:
        conn.execute(
            "INSERT INTO timesheet_entries (user_id, task_id, work_date, hours, description) VALUES (?,?,?,?,?)",
            (uid, tid, date, hours, desc),
        )

    conn.commit()
    print("Seed data created successfully.")
    print("  Admin:  admin / admin123")
    print("  LSP:    lsp_wang / lsp123")
    print("  SA:     sa_zhang / sa123")
    print("  SP:     sp_li / sp123")
