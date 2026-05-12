"""Hours validation utility."""


def validate_hours(hours: float) -> tuple[bool, str]:
    """Validate hours input. Returns (is_valid, message)."""
    if hours <= 0:
        return False, "Hours must be greater than 0."
    if hours > 24:
        return False, "Hours cannot exceed 24 in a single day."
    if hours > 12:
        return True, "Warning: You logged more than 12 hours in one day."
    return True, ""
