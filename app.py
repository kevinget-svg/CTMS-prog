"""CTMS STAT — Clinical Trial Management System for Statistics & Programming.

Entry point for the Streamlit multi-page application.
"""

import streamlit as st
from database.connection import init as db_init
from auth.auth_manager import get_current_user, require_auth
from auth.permissions import get_rank
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="CTMS STAT",
    page_icon=":material/clinical_notes:",
    layout="wide",
)

# Initialize database on first run
db_init()

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
    st.Page("pages/04_File_Manager.py", title="File Manager", icon=":material/folder:"),
    st.Page("pages/05_QC_Review.py", title="QC Review", icon=":material/rate_review:"),
]

if rank >= 30:  # LSP, Admin
    all_pages.append(
        st.Page("pages/08_Projects.py", title="Projects", icon=":material/folder_managed:")
    )
    all_pages.append(
        st.Page("pages/06_Team_Dashboard.py", title="Team Dashboard", icon=":material/group:")
    )
if rank >= 40:  # Admin only
    all_pages.append(
        st.Page("pages/07_Admin.py", title="Admin", icon=":material/admin_panel_settings:")
    )

pg = st.navigation(all_pages, position="sidebar", expanded=True)
pg.run()
