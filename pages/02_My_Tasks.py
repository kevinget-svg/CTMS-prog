"""My Tasks page — list view with inline drill-down and summary panel."""

import streamlit as st
from datetime import date
from auth.auth_manager import get_current_user
from auth.permissions import get_rank
from models import task as task_model
from models import user as user_model
from models import project as project_model
from services.task_service import change_status, get_allowed_transitions, get_status_badge

user = get_current_user()
rank = get_rank(user)
effective_rank = st.session_state.get("effective_role_rank", rank)

st.title("My Tasks")

# --- Summary Panel ---
tasks = task_model.get_tasks_for_user(user, project_id=st.session_state.get("selected_project_id"))

status_order = ["Not Started", "In Progress", "Awaiting QC", "QC In Review", "Revision Needed", "Complete"]
status_colors = {
    "Not Started":    "#9E9E9E",
    "In Progress":    "#1565C0",
    "Awaiting QC":    "#E65100",
    "QC In Review":   "#7B1FA2",
    "Revision Needed": "#C62828",
    "Complete":       "#2E7D32",
}
status_counts = {s: sum(1 for t in tasks if t["status"] == s) for s in status_order}
total = len(tasks)

# Summary bar chart
bar_html = "<div style='display:flex;align-items:center;height:28px;border-radius:6px;overflow:hidden;gap:2px;margin:8px 0;'>"
for s in status_order:
    count = status_counts[s]
    if count > 0:
        pct = count / max(total, 1) * 100
        bar_html += f"<div title='{s}: {count}' style='height:100%;width:{pct}%;background:{status_colors[s]};'></div>"
bar_html += "</div>"

# Legend
legend_parts = []
for s in status_order:
    legend_parts.append(f"<span style='display:inline-flex;align-items:center;gap:4px;margin-right:14px;'>"
                        f"<span style='width:10px;height:10px;border-radius:2px;background:{status_colors[s]};display:inline-block;'></span>"
                        f"{s} <b>{status_counts[s]}</b></span>")
legend_html = "".join(legend_parts)

col1, col2 = st.columns([2, 1])
with col1:
    st.html(f"""
    <div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px 20px;">
        <div style="font-size:14px;color:#666;margin-bottom:4px;">Task Summary</div>
        <div style="font-size:32px;font-weight:700;">{total} <span style="font-size:16px;font-weight:400;color:#888;">tasks</span></div>
        {bar_html}
        <div style="font-size:12px;margin-top:4px;">{legend_html}</div>
    </div>
    """)
with col2:
    completed = status_counts["Complete"]
    in_progress = status_counts["In Progress"]
    in_qc = status_counts["Awaiting QC"] + status_counts["QC In Review"]
    overdue_count = sum(1 for t in tasks if t["due_date"] and t["due_date"] < str(date.today()) and t["status"] != "Complete")
    st.html(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;text-align:center;">
            <div style="font-size:12px;color:#666;">Complete</div>
            <div style="font-size:24px;font-weight:700;color:#2E7D32;">{completed}</div>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;text-align:center;">
            <div style="font-size:12px;color:#666;">In Progress</div>
            <div style="font-size:24px;font-weight:700;color:#1565C0;">{in_progress}</div>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;text-align:center;">
            <div style="font-size:12px;color:#666;">In QC</div>
            <div style="font-size:24px;font-weight:700;color:#E65100;">{in_qc}</div>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;text-align:center;">
            <div style="font-size:12px;color:#666;">Overdue</div>
            <div style="font-size:24px;font-weight:700;color:#C62828;">{overdue_count}</div>
        </div>
    </div>
    """)

st.divider()

# --- Filters ---
categories = task_model.get_categories()
category_filter_map = {0: "All Categories"}
category_filter_map.update({c["id"]: c["name"] for c in categories})

col1, col2, col3, col4 = st.columns(4)
with col1:
    filter_category = st.selectbox("Category", options=list(category_filter_map.keys()),
                                   format_func=lambda x: category_filter_map[x])
with col2:
    filter_status = st.selectbox("Status", ["All", "Not Started", "In Progress",
                                 "Awaiting QC", "QC In Review", "Revision Needed", "Complete"])
with col3:
    filter_priority = st.selectbox("Priority", ["All", "Critical", "High", "Normal", "Low"])
with col4:
    projects = project_model.get_projects_for_user(user["id"])
    project_opts = {0: "All Projects"}
    project_opts.update({p["id"]: p["protocol_number"] for p in projects})
    filter_project = st.selectbox("Project", options=list(project_opts.keys()),
                                  format_func=lambda x: project_opts[x])

# Apply filters
if filter_category != 0:
    cat_subtypes = task_model.get_subtypes(filter_category)
    cat_sub_ids = {s["id"] for s in cat_subtypes}
    tasks = [t for t in tasks if t["subtype_id"] in cat_sub_ids]
if filter_status != "All":
    tasks = [t for t in tasks if t["status"] == filter_status]
if filter_priority != "All":
    tasks = [t for t in tasks if t["priority"] == filter_priority]
if filter_project != 0:
    tasks = [t for t in tasks if t["project_id"] == filter_project]

# --- New Task Form (LSP/Admin only) ---
if effective_rank >= 30:
    with st.expander("Create New Task", icon=":material/add_task:"):
        selected_pid = st.session_state.get("selected_project_id")
        if selected_pid:
            project_members = project_model.get_members(selected_pid)
            assignable = [m for m in project_members if m["role_rank"] <= 25]
            reviewers = [m for m in project_members if m["role_rank"] >= 25]
        else:
            all_users = user_model.get_all()
            all_roles = user_model.get_all_roles()
            sp_rank_ids = [r["id"] for r in all_roles if r["rank"] <= 25]
            reviewer_rank_ids = [r["id"] for r in all_roles if r["rank"] >= 25]
            assignable = [u for u in all_users if u["role_id"] in sp_rank_ids]
            reviewers = [u for u in all_users if u["role_id"] in reviewer_rank_ids]

        if "new_task_cat" not in st.session_state:
            st.session_state.new_task_cat = categories[0]["id"]

        selected_cat = st.selectbox(
            "Task Category",
            options=[c["id"] for c in categories],
            format_func=lambda x: next((c["name"] for c in categories if c["id"] == x), ""),
            key="new_task_cat",
        )
        subtypes = task_model.get_subtypes(selected_cat)

        with st.form("new_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                proj_list = project_model.get_all()
                task_project = st.selectbox("Project",
                    options=[p["id"] for p in proj_list],
                    format_func=lambda x: next((p["protocol_number"] for p in proj_list if p["id"] == x), ""))
                task_title = st.text_input("Task Title")
                task_desc = st.text_area("Description")
                task_subtype = st.selectbox("Task Subtype",
                    options=[s["id"] for s in subtypes],
                    format_func=lambda x: next((f"{s['code']} — {s['name']}" for s in subtypes if s["id"] == x), ""))
            with col2:
                task_assignee = st.selectbox("Assign To",
                    options=[u["id"] for u in assignable],
                    format_func=lambda x: next((u["full_name"] for u in assignable if u["id"] == x), ""))
                task_reviewer = st.selectbox("Reviewer",
                    options=[0] + [u["id"] for u in reviewers],
                    format_func=lambda x: "None" if x == 0 else next((u["full_name"] for u in reviewers if u["id"] == x), ""))
                task_priority = st.selectbox("Priority", ["Normal", "High", "Critical", "Low"])
                task_due = st.date_input("Due Date")
                task_est = st.number_input("Estimated Hours", min_value=0.0, step=0.5)

            if st.form_submit_button("Create Task", use_container_width=True):
                if task_title:
                    task_model.create(
                        project_id=task_project, title=task_title,
                        assigned_to=task_assignee,
                        reviewer_id=task_reviewer if task_reviewer != 0 else None,
                        description=task_desc, subtype_id=task_subtype,
                        priority=task_priority, due_date=str(task_due),
                        estimated_hours=task_est if task_est > 0 else None,
                    )
                    st.success("Task created.")
                    st.rerun()
                else:
                    st.error("Task title is required.")

st.divider()

# --- Task List with drill-down ---
if not tasks:
    st.info("No tasks found matching the current filters.")
else:
    st.caption(f"Showing {len(tasks)} task(s)")

    for t in tasks:
        type_label = f"{t['category_name']}/{t['subtype_code']}" if t["subtype_code"] else ""

        # Build a compact summary line
        status_bg = status_colors.get(t["status"], "#9E9E9E")
        row_html = f"""
        <div style="display:flex;align-items:center;gap:12px;padding:2px 0;">
            <span style="background:{status_bg};color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap;">{t['status']}</span>
            <span style="font-size:14px;font-weight:600;flex:1;">{t['title']}</span>
            <span style="font-size:12px;color:#888;">{type_label}</span>
            <span style="font-size:12px;color:#888;">{t['protocol_number'] or ''}</span>
            <span style="font-size:12px;color:#666;">{t['assignee_name']}</span>
            <span style="font-size:12px;color:#888;">{t['due_date'] or ''}</span>
        </div>
        """

        with st.expander(f"{t['status']} | {t['title']} | {type_label} | {t['assignee_name']}", expanded=False):
            # --- Detail section (drill-down) ---
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Project:** {t['protocol_number']} — {t['study_name']}")
                if t["subtype_code"]:
                    st.write(f"**Type:** {t['category_name']} → {t['subtype_code']} — {t['subtype_name']}")
                if t["reviewer_name"]:
                    st.write(f"**Reviewer:** {t['reviewer_name']}")
                st.write(f"**Description:** {t['description'] or 'None'}")

            with col2:
                st.write(f"**Status:** {get_status_badge(t['status'])}")
                st.write(f"**Priority:** {t['priority']}")
                st.write(f"**Due Date:** {t['due_date'] or 'N/A'}")
                st.write(f"**Est. Hours:** {t['estimated_hours'] or 'N/A'}")

            with col3:
                st.write(f"**Created:** {t['created_at'][:10]}")
                st.write(f"**Updated:** {t['updated_at'][:10]}")

            # Status actions
            allowed = get_allowed_transitions(t["status"])
            if allowed:
                st.divider()
                action_cols = st.columns(len(allowed))
                for i, new_status in enumerate(allowed):
                    with action_cols[i]:
                        if st.button(f"→ {new_status}", key=f"act_{t['id']}_{new_status}",
                                     type="primary" if new_status == "Complete" else "secondary",
                                     use_container_width=True):
                            if change_status(t["id"], new_status):
                                st.success(f"Status: {t['status']} → {new_status}")
                                st.rerun()
