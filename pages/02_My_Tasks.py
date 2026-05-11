"""My Tasks page — view and manage assigned tasks."""

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

st.title("My Tasks")

# --- Filters ---
col1, col2, col3 = st.columns(3)
with col1:
    filter_status = st.selectbox(
        "Status Filter",
        ["All", "Not Started", "In Progress", "Awaiting QC", "QC In Review", "Revision Needed", "Complete"],
    )
with col2:
    filter_priority = st.selectbox(
        "Priority Filter",
        ["All", "Critical", "High", "Normal", "Low"],
    )
with col3:
    projects = project_model.get_projects_for_user(user["id"])
    project_opts = {0: "All Projects"}
    project_opts.update({p["id"]: p["protocol_number"] for p in projects})
    filter_project = st.selectbox(
        "Project Filter",
        options=list(project_opts.keys()),
        format_func=lambda x: project_opts[x],
    )

st.divider()

# --- New Task Form (Manager/Admin only) ---
if rank >= 30:
    all_users = user_model.get_all()
    all_roles = user_model.get_all_roles()
    programmer_ranks = [r["id"] for r in all_roles if r["rank"] <= 20]  # rank <= 20: Programmers, Reviewers
    reviewer_ranks = [r["id"] for r in all_roles if r["rank"] >= 20]    # rank >= 20: Reviewers, Managers

    assignable_users = [u for u in all_users if u["role_id"] in programmer_ranks]
    reviewer_users = [u for u in all_users if u["role_id"] in reviewer_ranks]

    with st.expander("Create New Task", icon=":material/add_task:"):
        with st.form("new_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                proj_list = project_model.get_all()
                task_project = st.selectbox(
                    "Project",
                    options=[p["id"] for p in proj_list],
                    format_func=lambda x: next((p["protocol_number"] for p in proj_list if p["id"] == x), ""),
                )
                task_title = st.text_input("Task Title")
                task_desc = st.text_area("Description")
            with col2:
                task_assignee = st.selectbox(
                    "Assign To",
                    options=[u["id"] for u in assignable_users],
                    format_func=lambda x: next((u["full_name"] for u in assignable_users if u["id"] == x), ""),
                )
                task_reviewer = st.selectbox(
                    "Reviewer",
                    options=[0] + [u["id"] for u in reviewer_users],
                    format_func=lambda x: "None" if x == 0 else next((u["full_name"] for u in reviewer_users if u["id"] == x), ""),
                )
                task_type = st.selectbox("Type", ["Table", "Figure", "Listing", "Analysis", "Other"])
                task_priority = st.selectbox("Priority", ["Normal", "High", "Critical", "Low"])
                task_due = st.date_input("Due Date")
                task_est = st.number_input("Estimated Hours", min_value=0.0, step=0.5)

            if st.form_submit_button("Create Task", use_container_width=True):
                if task_title:
                    task_model.create(
                        project_id=task_project,
                        title=task_title,
                        assigned_to=task_assignee,
                        reviewer_id=task_reviewer if task_reviewer != 0 else None,
                        description=task_desc,
                        tfl_type=task_type,
                        priority=task_priority,
                        due_date=str(task_due),
                        estimated_hours=task_est if task_est > 0 else None,
                    )
                    st.success("Task created.")
                    st.rerun()
                else:
                    st.error("Task title is required.")

    st.divider()

# --- Task List ---
tasks = task_model.get_tasks_for_user(user)

if filter_status != "All":
    tasks = [t for t in tasks if t["status"] == filter_status]
if filter_priority != "All":
    tasks = [t for t in tasks if t["priority"] == filter_priority]
if filter_project != 0:
    tasks = [t for t in tasks if t["project_id"] == filter_project]

if not tasks:
    st.info("No tasks found matching the current filters.")
else:
    for t in tasks:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{t['title']}**")
                st.caption(f"{t['protocol_number'] or 'N/A'} — {t['study_name'] or ''}")
            with col2:
                st.write(f"Assignee: {t['assignee_name']}")
                if t["reviewer_name"]:
                    st.caption(f"Reviewer: {t['reviewer_name']}")
            with col3:
                st.write(get_status_badge(t["status"]))
                st.caption(f"Priority: {t['priority']} | Due: {t['due_date'] or 'N/A'}")
            with col4:
                st.write("")

            allowed = get_allowed_transitions(t["status"])
            if allowed:
                cols = st.columns(len(allowed) + 1)
                for i, new_status in enumerate(allowed):
                    with cols[i]:
                        btn_type = "primary" if new_status == "Complete" else "secondary"
                        if st.button(f"→ {new_status}", key=f"status_{t['id']}_{new_status}", type=btn_type):
                            if change_status(t["id"], new_status):
                                st.success(f"Status changed to '{new_status}'.")
                                st.rerun()
                with cols[-1]:
                    if st.button("View", key=f"view_{t['id']}"):
                        st.session_state.view_task_id = t["id"]
                        st.rerun()

# --- Task Detail ---
if "view_task_id" in st.session_state and st.session_state.view_task_id:
    task_id = st.session_state.view_task_id
    task = task_model.get_by_id(task_id)
    if task:
        st.divider()
        st.subheader(f"Task Detail: {task['title']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Project:** {task['protocol_number']} — {task['study_name']}")
            st.write(f"**Assignee:** {task['assignee_name']}")
            st.write(f"**Reviewer:** {task['reviewer_name'] or 'Not assigned'}")
            st.write(f"**Status:** {get_status_badge(task['status'])}")
            st.write(f"**Priority:** {task['priority']}")
        with col2:
            st.write(f"**Type:** {task['tfl_type'] or 'N/A'}")
            st.write(f"**Due Date:** {task['due_date'] or 'N/A'}")
            st.write(f"**Estimated Hours:** {task['estimated_hours'] or 'N/A'}")
            st.write(f"**Created:** {task['created_at']}")
            st.write(f"**Updated:** {task['updated_at']}")

        st.write(f"**Description:** {task['description'] or 'None'}")

        if st.button("Close Detail", type="secondary"):
            del st.session_state.view_task_id
            st.rerun()
