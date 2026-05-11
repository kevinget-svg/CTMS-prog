"""My Tasks page — view and manage assigned tasks with CDISC domain types."""

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
categories = task_model.get_categories()
category_filter_map = {0: "All Categories"}
category_filter_map.update({c["id"]: c["name"] for c in categories})

col1, col2, col3, col4 = st.columns(4)
with col1:
    filter_category = st.selectbox(
        "Category",
        options=list(category_filter_map.keys()),
        format_func=lambda x: category_filter_map[x],
    )
with col2:
    filter_status = st.selectbox(
        "Status",
        ["All", "Not Started", "In Progress", "Awaiting QC", "QC In Review", "Revision Needed", "Complete"],
    )
with col3:
    filter_priority = st.selectbox(
        "Priority",
        ["All", "Critical", "High", "Normal", "Low"],
    )
with col4:
    projects = project_model.get_projects_for_user(user["id"])
    project_opts = {0: "All Projects"}
    project_opts.update({p["id"]: p["protocol_number"] for p in projects})
    filter_project = st.selectbox(
        "Project",
        options=list(project_opts.keys()),
        format_func=lambda x: project_opts[x],
    )

st.divider()

# --- New Task Form (LSP/Admin only, rank >= 30) ---
if rank >= 30:
    all_users = user_model.get_all()
    all_roles = user_model.get_all_roles()
    sp_rank_ids = [r["id"] for r in all_roles if r["rank"] <= 25]
    reviewer_rank_ids = [r["id"] for r in all_roles if r["rank"] >= 25]

    assignable = [u for u in all_users if u["role_id"] in sp_rank_ids]
    reviewers = [u for u in all_users if u["role_id"] in reviewer_rank_ids]

    with st.expander("Create New Task", icon=":material/add_task:"):
        # Category outside form so selection triggers rerun for subtype cascade
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
                task_project = st.selectbox(
                    "Project",
                    options=[p["id"] for p in proj_list],
                    format_func=lambda x: next((p["protocol_number"] for p in proj_list if p["id"] == x), ""),
                )
                task_title = st.text_input("Task Title")
                task_desc = st.text_area("Description")

                task_subtype = st.selectbox(
                    "Task Subtype",
                    options=[s["id"] for s in subtypes],
                    format_func=lambda x: next(
                        (f"{s['code']} — {s['name']}" for s in subtypes if s["id"] == x), ""
                    ),
                )

            with col2:
                task_assignee = st.selectbox(
                    "Assign To",
                    options=[u["id"] for u in assignable],
                    format_func=lambda x: next((u["full_name"] for u in assignable if u["id"] == x), ""),
                )
                task_reviewer = st.selectbox(
                    "Reviewer",
                    options=[0] + [u["id"] for u in reviewers],
                    format_func=lambda x: "None" if x == 0 else next((u["full_name"] for u in reviewers if u["id"] == x), ""),
                )
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
                        subtype_id=task_subtype,
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

# Filter by category
if filter_category != 0:
    # Get subtype IDs for this category
    cat_subtypes = task_model.get_subtypes(filter_category)
    cat_sub_ids = {s["id"] for s in cat_subtypes}
    tasks = [t for t in tasks if t["subtype_id"] in cat_sub_ids]

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
                type_label = f"{t['category_name']}/{t['subtype_code']}" if t["subtype_code"] else ""
                st.write(f"**{t['title']}**")
                st.caption(f"{type_label} | {t['protocol_number'] or 'N/A'}")
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
            st.write(f"**Type:** {task['category_name']} → {task['subtype_code']} — {task['subtype_name']}" if task["subtype_code"] else "**Type:** N/A")
            st.write(f"**Assignee:** {task['assignee_name']}")
            st.write(f"**Reviewer:** {task['reviewer_name'] or 'Not assigned'}")
            st.write(f"**Status:** {get_status_badge(task['status'])}")
            st.write(f"**Priority:** {task['priority']}")
        with col2:
            st.write(f"**Due Date:** {task['due_date'] or 'N/A'}")
            st.write(f"**Estimated Hours:** {task['estimated_hours'] or 'N/A'}")
            st.write(f"**Created:** {task['created_at']}")
            st.write(f"**Updated:** {task['updated_at']}")

        st.write(f"**Description:** {task['description'] or 'None'}")

        if st.button("Close Detail", type="secondary"):
            del st.session_state.view_task_id
            st.rerun()
