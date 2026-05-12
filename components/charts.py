"""Plotly chart helpers for dashboards."""

import plotly.express as px
import pandas as pd
from services.task_service import STATUS_COLORS


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
    fig = px.pie(
        df, names="Status", values="Count",
        title="Task Status Distribution",
        color="Status",
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


