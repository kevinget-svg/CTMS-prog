"""Plotly chart helpers for dashboards."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def hours_bar_chart(daily_hours: dict):
    """Bar chart of daily hours for a week."""
    if not daily_hours:
        return None
    df = pd.DataFrame([
        {"Date": date, "Hours": hours}
        for date, hours in daily_hours.items()
    ])
    fig = px.bar(
        df, x="Date", y="Hours",
        title="Daily Hours This Week",
        text_auto=True,
        color_discrete_sequence=["#1565C0"],
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def task_status_pie_chart(tasks: list):
    """Pie chart of task status distribution."""
    if not tasks:
        return None
    status_counts = {}
    for t in tasks:
        status = t["status"] if "status" in t.keys() else "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    df = pd.DataFrame([
        {"Status": k, "Count": v} for k, v in status_counts.items()
    ])
    colors = {
        "Not Started": "#9E9E9E", "In Progress": "#42A5F5",
        "Awaiting QC": "#FFA726", "QC In Review": "#AB47BC",
        "Revision Needed": "#EF5350", "Complete": "#66BB6A",
    }
    fig = px.pie(
        df, names="Status", values="Count",
        title="Task Status Distribution",
        color="Status",
        color_discrete_map=colors,
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def workload_bar_chart(user_hours: list):
    """Horizontal bar chart of per-user hours."""
    if not user_hours:
        return None
    df = pd.DataFrame([
        {"User": u["full_name"], "Hours": u["total_hours"]}
        for u in user_hours
    ])
    fig = px.bar(
        df, x="Hours", y="User", orientation="h",
        title="Workload by Person",
        text_auto=True,
        color_discrete_sequence=["#1565C0"],
    )
    fig.update_layout(height=max(200, len(df) * 50), margin=dict(l=20, r=20, t=40, b=20))
    return fig


def weekly_hours_line_chart(week_data: list):
    """Line chart of hours over days."""
    if not week_data:
        return None
    df = pd.DataFrame(week_data)
    fig = px.line(
        df, x="Date", y="Hours",
        title="Hours Trend",
        markers=True,
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig
