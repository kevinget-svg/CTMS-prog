"""Team Dashboard page — management view of team workload and project progress.

Phase 3 feature — coming soon.
"""

import streamlit as st
from auth.auth_manager import get_current_user

user = get_current_user()

st.title("Team Dashboard")
st.info("Team Dashboard will be available in Phase 3. Stay tuned!")
st.caption("Features: Team workload charts, project progress burndown, hours aggregation, CSV export.")
