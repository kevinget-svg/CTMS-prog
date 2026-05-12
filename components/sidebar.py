"""Sidebar component with user info, password change, and project filter."""

import streamlit as st
from auth.auth_manager import get_current_user, logout, change_password
from auth import permissions
from models import project as project_model


def render_sidebar():
    """Render the persistent sidebar with user info and project filter."""
    user = get_current_user()
    if user is None:
        return

    with st.sidebar:
        st.subheader(f"Welcome, {user['full_name']}")

        # Project filter stored in session state for cross-page persistence
        projects = project_model.get_projects_for_user(user["id"])
        project_options = {p["id"]: f"{p['protocol_number']} — {p['study_name']}" for p in projects}

        if project_options:
            if "selected_project_id" not in st.session_state:
                st.session_state.selected_project_id = list(project_options.keys())[0]

            st.session_state.selected_project_id = st.selectbox(
                "Active Project",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                key="sidebar_project_filter",
            )

        # --- Effective Role Display ---
        selected_id = st.session_state.get("selected_project_id")
        if selected_id:
            effective_name = permissions.get_effective_role_name(user, selected_id)
            effective_rank = permissions.get_effective_rank(user, selected_id)
            global_name = user["role_name"]
            if effective_name != global_name:
                st.caption(f"Role: **{effective_name}** (global: {global_name})")
            else:
                st.caption(f"Role: {effective_name}")
            st.session_state.effective_role_rank = effective_rank
            st.session_state.effective_role_name = effective_name
        else:
            st.caption(f"Role: {user['role_name']}")
            st.session_state.effective_role_rank = user["role_rank"]
            st.session_state.effective_role_name = user["role_name"]

        st.divider()

        # --- Change Password ---
        with st.expander("Change Password", icon=":material/lock:"):
            with st.form("change_password_form"):
                old_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password", type="password")
                confirm_pw = st.text_input("Confirm New Password", type="password")
                submitted = st.form_submit_button("Change Password", use_container_width=True)

                if submitted:
                    if not old_pw or not new_pw or not confirm_pw:
                        st.error("All fields are required.")
                    elif new_pw != confirm_pw:
                        st.error("New passwords do not match.")
                    else:
                        ok, msg = change_password(user["id"], old_pw, new_pw)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

        st.divider()
        st.button("Logout", on_click=logout, use_container_width=True, type="secondary")
