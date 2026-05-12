"""CTMS STAT — Clinical Trial Management System for Statistics & Programming.

Entry point for the Streamlit multi-page application.
"""

import streamlit as st
from database.connection import init
from auth.auth_manager import get_current_user, require_auth
from auth.permissions import get_rank
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="CTMS STAT",
    page_icon=":material/clinical_notes:",
    layout="wide",
)

# Initialize database on first run
init()

# Auth gate — stops rendering below until logged in
if not require_auth():
    st.stop()

user = get_current_user()
render_sidebar()

rank = get_rank(user)

# --- Rank-based page definitions ---
all_pages = [
    st.Page("pages/01_My_Dashboard.py", title="My Dashboard", icon=":material/dashboard:"),
    st.Page("pages/02_My_Tasks.py", title="My Tasks", icon=":material/assignment:"),
    st.Page("pages/03_Timesheet.py", title="Timesheet", icon=":material/schedule:"),
]

if rank >= 30:  # LSP, Admin
    all_pages.append(
        st.Page("pages/08_Projects.py", title="Projects", icon=":material/folder_managed:")
    )
if rank >= 40:  # Admin only
    all_pages.append(
        st.Page("pages/07_Admin.py", title="Admin", icon=":material/admin_panel_settings:")
    )

pg = st.navigation(all_pages, position="sidebar", expanded=True)
pg.run()
