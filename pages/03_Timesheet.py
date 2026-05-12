"""Timesheet page — daily work hours entry and weekly view."""

import streamlit as st
from datetime import date, timedelta
from auth.auth_manager import get_current_user
from models import task as task_model
from models import timesheet as ts_model
from services.hours_service import validate_hours
from components.charts import hours_bar_chart

user = get_current_user()

st.title("Timesheet")

# --- Daily Entry Form ---
with st.expander("Log Hours", expanded=True, icon=":material/edit_note:"):
    tasks = task_model.get_tasks_for_user(user, project_id=st.session_state.get("selected_project_id"))
    active_tasks = [t for t in tasks if t["status"] not in ("Complete",)]
    if not active_tasks:
        active_tasks = tasks

    if not active_tasks:
        st.warning("No tasks assigned yet. Ask your manager to create a task first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            work_date = st.date_input("Date", value=date.today(), max_value=date.today())
        with col2:
            task_id = st.selectbox(
                "Task",
                options=[t["id"] for t in active_tasks],
                format_func=lambda x: next(
                    (f"[{t['protocol_number']}] {t['title']}" for t in active_tasks if t["id"] == x), ""
                ),
            )

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            desc = st.text_area("What did you do?", placeholder="e.g., Wrote SAS program for demographics table")
        with col2:
            hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5, value=1.0)
        with col3:
            st.write("")
            st.write("")
            submitted = st.button("Save Entry", use_container_width=True, type="primary")

        if submitted:
            is_valid, msg = validate_hours(hours)
            if not is_valid:
                st.error(msg)
            else:
                ts_model.upsert_entry(user["id"], task_id, str(work_date), hours, desc)
                if msg:
                    st.warning(msg)
                else:
                    st.success(f"Logged {hours}h on {work_date}.")
                st.rerun()

st.divider()

# --- Weekly View ---
today = date.today()
monday = today - timedelta(days=today.weekday())

col1, col2 = st.columns([1, 3])
with col1:
    week_offset = st.selectbox(
        "Week",
        ["This Week", "Last Week", "2 Weeks Ago", "3 Weeks Ago"],
        index=0,
    )
    offset_map = {"This Week": 0, "Last Week": 1, "2 Weeks Ago": 2, "3 Weeks Ago": 3}
    offset = offset_map[week_offset]
    ws = monday - timedelta(weeks=offset)
    we = ws + timedelta(days=6)

weekly = ts_model.get_weekly_hours(user["id"], str(ws), str(we))
total_week = sum(weekly.values())

days_logged = len(weekly)
avg = total_week / days_logged if days_logged > 0 else 0

kpi_style = """
<style>
.kpi-grid { display: flex; gap: 16px; margin: 16px 0; }
.kpi-card { flex: 1; padding: 20px 24px; border-radius: 12px; border: 1px solid #e0e0e0; background: #fff; }
.kpi-label { font-size: 14px; color: #666; margin-bottom: 6px; }
.kpi-value { font-size: 36px; font-weight: 700; line-height: 1.1; }
.kpi-blue  .kpi-value { color: #1565C0; }
.kpi-green .kpi-value { color: #2E7D32; }
.kpi-teal  .kpi-value { color: #00695C; }
</style>
"""

kpi_html = f"""
{kpi_style}
<div class="kpi-grid">
    <div class="kpi-card kpi-blue">
        <div class="kpi-label">Week Total</div>
        <div class="kpi-value">{total_week:.1f}h</div>
    </div>
    <div class="kpi-card kpi-green">
        <div class="kpi-label">Days Logged</div>
        <div class="kpi-value">{days_logged}</div>
    </div>
    <div class="kpi-card kpi-teal">
        <div class="kpi-label">Avg Hours / Day</div>
        <div class="kpi-value">{avg:.1f}h</div>
    </div>
</div>
"""
st.html(kpi_html)

st.subheader(f"Week of {ws} to {we}")

fig = hours_bar_chart(weekly)
if fig:
    st.plotly_chart(fig, use_container_width=True)

entries = ts_model.get_by_user_date_range(user["id"], str(ws), str(we))
weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

if entries:
    entries_by_date = {}
    for e in entries:
        d = e["work_date"]
        if d not in entries_by_date:
            entries_by_date[d] = []
        entries_by_date[d].append(e)

    for day_offset in range(7):
        d = ws + timedelta(days=day_offset)
        d_str = str(d)
        day_label = f"{weekdays[day_offset]} {d_str}"
        if d_str in entries_by_date:
            for e in entries_by_date[d_str]:
                st.write(f"**{day_label}** — {e['task_title']} — {e['hours']}h — {e['description'] or ''}")
        else:
            st.caption(f"{day_label} — No entries")
else:
    st.info("No timesheet entries for this week.")
