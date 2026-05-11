"""File Manager page — upload and manage SAS/R code and output files.

Phase 2 feature — coming soon.
"""

import streamlit as st
from auth.auth_manager import get_current_user

user = get_current_user()

st.title("File Manager")
st.info("File Manager will be available in Phase 2. Stay tuned!")
st.caption("Features: Upload SAS/R programs, output files (PDF/RTF/Excel), version tracking, double-programming flag.")
