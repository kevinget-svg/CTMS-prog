"""Hours aggregation and validation service."""

from models import timesheet as ts_model


def get_personal_week_summary(user_id: int, week_start: str, week_end: str):
    """Get daily hours breakdown for a week."""
    return ts_model.get_weekly_hours(user_id, week_start, week_end)


def get_personal_month_summary(user_id: int, year: int, month: int):
    """Get detailed timesheet entries for a month."""
    return ts_model.get_monthly_aggregation(user_id, year, month)


def get_team_summary(date_from: str, date_to: str, project_id: int = None):
    """Get all timesheet entries for management view."""
    return ts_model.get_all_entries(date_from, date_to, project_id)


def get_project_workload(project_id: int, date_from: str = None, date_to: str = None):
    """Get per-user hours aggregation for a project."""
    return ts_model.get_project_hours(project_id, date_from, date_to)


def validate_hours(hours: float) -> tuple[bool, str]:
    """Validate hours input. Returns (is_valid, message)."""
    if hours <= 0:
        return False, "Hours must be greater than 0."
    if hours > 24:
        return False, "Hours cannot exceed 24 in a single day."
    if hours > 12:
        return True, "Warning: You logged more than 12 hours in one day."
    return True, ""
