"""QC Review page — formal review workflow for Reviewers.

Phase 2 feature — coming soon.
"""

import streamlit as st
from auth.auth_manager import get_current_user

user = get_current_user()

st.title("QC Review")
st.info("QC Review will be available in Phase 2. Stay tuned!")
st.caption("Features: Review queue, approve/reject with comments, side-by-side output comparison.")
