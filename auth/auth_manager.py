"""Authentication manager for CTMS STAT.

Uses bcrypt for password hashing and st.session_state for session persistence.
"""

import bcrypt
import streamlit as st
from database.connection import get_db


def authenticate(username: str, password: str) -> dict | None:
    """Verify credentials and return user dict with role info, or None."""
    db = get_db()
    user = db.execute(
        """SELECT u.*, r.name as role_name, r.rank as role_rank
           FROM users u JOIN roles r ON u.role_id = r.id
           WHERE u.username = ? AND u.is_active = 1""",
        (username,),
    ).fetchone()
    if user is None:
        return None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return dict(user)
    return None


def get_current_user() -> dict | None:
    """Return current authenticated user from session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        return None
    return st.session_state.get("user")


def require_auth() -> bool:
    """Ensure user is authenticated. Returns True if authenticated, False otherwise.

    When False, renders the login form and returns False.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        _render_login_form()
        return False
    return True


def logout():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.session_state.user = None


def change_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    """Change password for a user. Returns (success, message)."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        return False, "User not found."
    if not bcrypt.checkpw(old_password.encode(), user["password_hash"].encode()):
        return False, "Current password is incorrect."
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters."
    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    db.commit()
    return True, "Password changed successfully."


def _render_login_form():
    """Render centered login form."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CTMS STAT")
        st.caption("Clinical Trial Management System — Statistics")
        st.divider()

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")
