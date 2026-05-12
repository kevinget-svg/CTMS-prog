"""Shared project form component."""

import streamlit as st
from models import project as project_model


def render_create_project_form():
    """Render a collapsible 'Create New Project' form. Returns nothing."""
    with st.expander("Create New Project", icon=":material/create_new_folder:"):
        with st.form("create_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                protocol = st.text_input("Protocol Number", placeholder="e.g., ABC-123-001")
                study = st.text_input("Study Name", placeholder="e.g., Phase III Study in Psoriasis")
            with col2:
                sponsor = st.text_input("Sponsor", placeholder="e.g., ABC Pharma")
                desc = st.text_area("Description")
            if st.form_submit_button("Create Project", use_container_width=True):
                if protocol and study:
                    project_model.create(protocol, study, sponsor or None, desc or None)
                    st.success(f"Project '{protocol}' created.")
                    st.rerun()
                else:
                    st.error("Protocol number and study name are required.")
