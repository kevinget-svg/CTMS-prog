"""Task business logic — status state machine and workflow."""

import streamlit as st
from models import task as task_model

ALLOWED_TRANSITIONS = {
    "Not Started":    ["In Progress"],
    "In Progress":    ["Awaiting QC"],
    "Awaiting QC":    ["QC In Review"],
    "QC In Review":   ["Complete", "Revision Needed"],
    "Revision Needed": ["In Progress"],
}

STATUS_DISPLAY = {
    "Not Started":    ":gray[Not Started]",
    "In Progress":    ":blue[In Progress]",
    "Awaiting QC":    ":orange[Awaiting QC]",
    "QC In Review":   ":violet[QC In Review]",
    "Revision Needed": ":red[Revision Needed]",
    "Complete":       ":green[Complete]",
}


def get_allowed_transitions(current_status: str) -> list:
    """Return list of valid next statuses from current status."""
    return ALLOWED_TRANSITIONS.get(current_status, [])


def can_transition(current_status: str, new_status: str) -> bool:
    """Check if a status transition is valid."""
    return new_status in ALLOWED_TRANSITIONS.get(current_status, [])


def change_status(task_id: int, new_status: str) -> bool:
    """Attempt a status transition. Returns True if successful."""
    task = task_model.get_by_id(task_id)
    if task is None:
        st.error("Task not found.")
        return False
    if not can_transition(task["status"], new_status):
        st.error(f"Cannot transition from '{task['status']}' to '{new_status}'.")
        return False
    task_model.update_status(task_id, new_status)
    return True


def get_status_badge(status: str) -> str:
    """Return colored markdown badge for a status."""
    colors = {
        "Not Started": "gray",
        "In Progress": "blue",
        "Awaiting QC": "orange",
        "QC In Review": "violet",
        "Revision Needed": "red",
        "Complete": "green",
    }
    color = colors.get(status, "gray")
    return f":{color}[{status}]"
