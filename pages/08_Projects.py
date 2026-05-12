"""Project Management page — accessible to LSP and Admin."""

import streamlit as st
from auth.auth_manager import get_current_user
from auth.permissions import get_rank, can_manage_projects
from models import user as user_model
from models import project as project_model

user = get_current_user()
if not user or get_rank(user) < 30:
    st.error("Access denied. LSP or Admin only.")
    st.stop()

st.title("Project Management")

# --- Create Project ---
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

st.divider()

# --- Project List ---
projects = project_model.get_all()
if not projects:
    st.info("No projects yet. Create one above.")
else:
    for p in projects:
        with st.expander(f"{p['protocol_number']} — {p['study_name']} ({p['status']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sponsor:** {p['sponsor'] or 'N/A'}")
                st.write(f"**Description:** {p['description'] or 'N/A'}")
                st.write(f"**Created:** {p['created_at']}")

                members = project_model.get_members(p["id"])
                member_names = [f"{m['full_name']} ({m['role_name']})" for m in members]
                st.write(f"**Members:** {', '.join(member_names)}")

            with col2:
                new_status = st.selectbox(
                    "Status", ["Active", "Completed", "On Hold"],
                    key=f"status_{p['id']}",
                    index=["Active", "Completed", "On Hold"].index(p["status"]),
                )
                if st.button("Update Status", key=f"upd_{p['id']}"):
                    project_model.update_status(p["id"], new_status)
                    st.rerun()

                st.divider()

                all_users = user_model.get_all()
                all_roles = user_model.get_all_roles()
                current_member_ids = {m["id"] for m in members}
                available = [u for u in all_users if u["id"] not in current_member_ids]
                if available:
                    add_user_id = st.selectbox(
                        "Add Member",
                        options=[u["id"] for u in available],
                        format_func=lambda x, avail=available: next((u["full_name"] for u in avail if u["id"] == x), ""),
                        key=f"add_{p['id']}",
                    )
                    add_role_id = st.selectbox(
                        "Role",
                        options=[r["id"] for r in all_roles],
                        format_func=lambda x: next((r["name"] for r in all_roles if r["id"] == x), ""),
                        key=f"addrole_{p['id']}",
                    )
                    if st.button("Add to Project", key=f"addbtn_{p['id']}"):
                        project_model.add_member(p["id"], add_user_id, add_role_id)
                        st.rerun()

                # Remove member
                if members:
                    remove_user_id = st.selectbox(
                        "Remove Member",
                        options=[m["id"] for m in members],
                        format_func=lambda x: next((f"{m['full_name']} ({m['role_name']})" for m in members if m["id"] == x), ""),
                        key=f"rm_{p['id']}",
                    )
                    if st.button("Remove from Project", key=f"rmbtn_{p['id']}", type="secondary"):
                        project_model.remove_member(p["id"], remove_user_id)
                        st.rerun()
