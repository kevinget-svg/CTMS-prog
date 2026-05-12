"""My Dashboard page — personal KPIs and summary."""

import streamlit as st
from datetime import date, timedelta
from auth.auth_manager import get_current_user
from models import task as task_model
from models import timesheet as ts_model
from models import project as project_model
from components.charts import hours_bar_chart, task_status_pie_chart
from components.kpi_card import render_kpi_cards

user = get_current_user()

st.title(f"My Dashboard")

# --- KPI Cards ---
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)
week_start = str(monday)
week_end = str(sunday)

tasks = task_model.get_tasks_for_user(user, project_id=st.session_state.get("selected_project_id"))
weekly_hours = ts_model.get_weekly_hours(user["id"], week_start, week_end)
total_week = sum(weekly_hours.values())

in_progress = sum(1 for t in tasks if t["status"] == "In Progress")
awaiting_qc = sum(1 for t in tasks if t["status"] in ("Awaiting QC", "QC In Review"))
overdue = sum(1 for t in tasks if t["due_date"] and t["due_date"] < str(today) and t["status"] != "Complete")
total_tasks = len(tasks)
complete_tasks = sum(1 for t in tasks if t["status"] == "Complete")

render_kpi_cards([
    {"label": "In Progress", "value": str(in_progress), "color": "blue",
     "sub": f"{complete_tasks} completed / {total_tasks} total tasks"},
    {"label": "In QC Review", "value": str(awaiting_qc), "color": "orange",
     "sub": "Awaiting or under QC review"},
    {"label": "Overdue", "value": str(overdue), "color": "red",
     "sub": "Past due date, not yet completed"},
    {"label": "Hours This Week", "value": f'{total_week:.1f}<span style="font-size:20px;color:#888;"> h</span>', "color": "green",
     "sub": f"{len(weekly_hours)} days logged this week"},
])

st.divider()

# --- My Projects ---
st.subheader("My Projects")
projects = project_model.get_projects_for_user(user["id"])
if projects:
    cols = st.columns(len(projects))
    for i, p in enumerate(projects):
        with cols[i]:
            p_tasks = [t for t in tasks if t["project_id"] == p["id"]]
            p_complete = sum(1 for t in p_tasks if t["status"] == "Complete")
            p_total = len(p_tasks)
            with st.container(border=True):
                st.write(f"**{p['protocol_number']}**")
                st.caption(p["study_name"])
                st.write(f"Tasks: {p_complete}/{p_total}")
                if p_total > 0:
                    st.progress(p_complete / p_total)

st.divider()

# --- My Tasks (top 8) ---
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Active Tasks")
    active_tasks = [t for t in tasks if t["status"] != "Complete"][:8]
    if active_tasks:
        for t in active_tasks:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{t['title']}**")
                    due = t["due_date"] or "No due date"
                    st.caption(f"{t['protocol_number']} | Due: {due} | {t['status']}")
                with c2:
                    st.caption(f"{t['priority']}")
    else:
        st.info("No active tasks.")

with col2:
    st.subheader("Task Status")
    fig = task_status_pie_chart(tasks)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- This Week's Hours ---
st.subheader("Hours This Week")
if weekly_hours:
    fig = hours_bar_chart(weekly_hours)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hours logged this week yet.")

# --- Recent Timesheet Entries ---
st.divider()
st.subheader("Recent Time Entries")
recent = ts_model.get_by_user_date_range(user["id"], str(today - timedelta(days=14)), str(today))
if recent:
    for e in recent[:5]:
        st.write(f"**{e['work_date']}** — {e['task_title']} — {e['hours']}h — {e['description'] or ''}")
else:
    st.info("No recent timesheet entries.")
