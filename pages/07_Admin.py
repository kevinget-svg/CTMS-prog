"""Admin page — user management, project management, role management."""

import bcrypt
import streamlit as st
from auth.auth_manager import get_current_user
from auth.permissions import get_rank
from models import user as user_model
from models import project as project_model
from database.connection import get_db

user = get_current_user()
if not user or get_rank(user) < 40:
    st.error("Access denied. Admin only.")
    st.stop()

st.title("Admin Panel")

tab1, tab2, tab3, tab4 = st.tabs(["Users", "Projects", "Roles", "Database"])

# --- Users Tab ---
with tab1:
    st.subheader("User Management")

    roles = user_model.get_all_roles()

    with st.expander("Create New User", icon=":material/person_add:"):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_fullname = st.text_input("Full Name")
            with col2:
                new_email = st.text_input("Email")
                new_role_id = st.selectbox(
                    "Role",
                    options=[r["id"] for r in roles],
                    format_func=lambda x: f"{next((r['name'] for r in roles if r['id'] == x), '')} (rank: {next((r['rank'] for r in roles if r['id'] == x), '')})",
                )
            if st.form_submit_button("Create User", use_container_width=True):
                if new_username and new_password and new_fullname:
                    existing = user_model.get_by_username(new_username)
                    if existing:
                        st.error(f"Username '{new_username}' already exists.")
                    else:
                        pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                        user_model.create(new_username, pw_hash, new_fullname, new_role_id, new_email or None)
                        st.success(f"User '{new_username}' created.")
                        st.rerun()
                else:
                    st.error("Username, password, and full name are required.")

    st.divider()
    users = user_model.get_all(include_inactive=True)
    if users:
        st.dataframe(
            [
                {"ID": u["id"], "Username": u["username"], "Full Name": u["full_name"],
                 "Email": u["email"] or "", "Role": u["role_name"],
                 "Active": "Yes" if u["is_active"] else "No"}
                for u in users
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.caption("Update role or deactivate/reactivate user:")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            non_admin_users = [u for u in users if u["username"] != "admin"]
            selected_user_id = st.selectbox(
                "Select User",
                options=[u["id"] for u in non_admin_users],
                format_func=lambda x: next((u["full_name"] for u in non_admin_users if u["id"] == x), ""),
            )
        with col2:
            target_user = next((u for u in users if u["id"] == selected_user_id), None)
            current_role_id = target_user["role_id"] if target_user else roles[0]["id"]
            role_index = next((i for i, r in enumerate(roles) if r["id"] == current_role_id), 0)
            new_role_id = st.selectbox(
                "New Role",
                options=[r["id"] for r in roles],
                format_func=lambda x: next((r["name"] for r in roles if r["id"] == x), ""),
                index=role_index,
            )
        with col3:
            if st.button("Update Role"):
                if target_user:
                    user_model.update_role(selected_user_id, new_role_id)
                    st.success("Role updated.")
                    st.rerun()

        col1, col2, _ = st.columns([2, 2, 2])
        with col1:
            if st.button("Deactivate User", type="secondary"):
                if target_user and target_user["is_active"]:
                    user_model.deactivate(selected_user_id)
                    st.warning(f"User '{target_user['full_name']}' deactivated.")
                    st.rerun()
        with col2:
            if st.button("Reactivate User", type="secondary"):
                db = get_db()
                db.execute("UPDATE users SET is_active = 1 WHERE id = ?", (selected_user_id,))
                db.commit()
                st.success("User reactivated.")
                st.rerun()

# --- Projects Tab ---
with tab2:
    st.subheader("Project Management")

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
    projects = project_model.get_all()
    if projects:
        for p in projects:
            with st.expander(f"{p['protocol_number']} — {p['study_name']} ({p['status']})"):
                st.write(f"**Sponsor:** {p['sponsor'] or 'N/A'}")
                st.write(f"**Description:** {p['description'] or 'N/A'}")
                st.write(f"**Created:** {p['created_at']}")

                members = project_model.get_members(p["id"])
                st.caption(f"Members: {', '.join(m['full_name'] for m in members)}")

                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox(
                        "Status", ["Active", "Completed", "On Hold"],
                        key=f"status_{p['id']}",
                        index=["Active", "Completed", "On Hold"].index(p["status"]),
                    )
                    if st.button("Update Status", key=f"upd_{p['id']}"):
                        project_model.update_status(p["id"], new_status)
                        st.rerun()
                with col2:
                    all_users = user_model.get_all()
                    current_member_ids = {m["id"] for m in members}
                    available = [u for u in all_users if u["id"] not in current_member_ids]
                    if available:
                        add_user_id = st.selectbox(
                            "Add Member",
                            options=[u["id"] for u in available],
                            format_func=lambda x, avail=available: next((u["full_name"] for u in avail if u["id"] == x), ""),
                            key=f"add_{p['id']}",
                        )
                        if st.button("Add to Project", key=f"addbtn_{p['id']}"):
                            project_model.add_member(p["id"], add_user_id)
                            st.rerun()

# --- Roles Tab ---
with tab3:
    st.subheader("Role Management")
    st.caption("Define roles and their permission ranks. Higher rank = more permissions.")

    current_roles = user_model.get_all_roles()

    # Display existing roles
    st.write("**Current Roles**")
    if current_roles:
        st.dataframe(
            [
                {"ID": r["id"], "Name": r["name"], "Rank": r["rank"], "Description": r["description"] or ""}
                for r in current_roles
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Rank 10=Programmer, 20=Reviewer, 30=Manager, 40=Admin")

    st.divider()

    # Create new role
    with st.expander("Create New Role", icon=":material/add_circle:"):
        with st.form("create_role_form"):
            col1, col2 = st.columns(2)
            with col1:
                role_name = st.text_input("Role Name", placeholder="e.g., Lead Programmer")
                role_rank = st.number_input("Rank", min_value=5, max_value=100, value=15, step=5,
                                            help="Higher = more permissions. 10=Programmer, 20=Reviewer, 30=Manager, 40=Admin")
            with col2:
                role_desc = st.text_area("Description", placeholder="e.g., Senior statistical programmer with review ability")
            if st.form_submit_button("Create Role", use_container_width=True):
                if role_name:
                    existing_role = db.execute("SELECT id FROM roles WHERE name = ?", (role_name,)).fetchone()
                    if existing_role:
                        st.error(f"Role '{role_name}' already exists.")
                    else:
                        user_model.create_role(role_name, role_rank, role_desc or None)
                        st.success(f"Role '{role_name}' created.")
                        st.rerun()
                else:
                    st.error("Role name is required.")

    # Edit/delete existing roles
    if current_roles:
        st.divider()
        st.write("**Edit or Delete Role**")
        edit_role_id = st.selectbox(
            "Select Role to Edit",
            options=[r["id"] for r in current_roles],
            format_func=lambda x: next((r["name"] for r in current_roles if r["id"] == x), ""),
        )
        selected_role = next((r for r in current_roles if r["id"] == edit_role_id), None)

        if selected_role:
            col1, col2, col3 = st.columns(3)
            with col1:
                edit_name = st.text_input("Name", value=selected_role["name"], key="edit_role_name")
            with col2:
                edit_rank = st.number_input("Rank", value=selected_role["rank"], step=5, key="edit_role_rank")
            with col3:
                edit_desc = st.text_input("Description", value=selected_role["description"] or "", key="edit_role_desc")

            col1, col2, _ = st.columns([1, 1, 4])
            with col1:
                if st.button("Save Changes", type="primary"):
                    user_model.update_role_info(edit_role_id, edit_name, edit_rank, edit_desc)
                    st.success("Role updated.")
                    st.rerun()
            with col2:
                if st.button("Delete Role", type="secondary"):
                    ok, msg = user_model.delete_role(edit_role_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# --- Database Tab ---
with tab4:
    st.subheader("Database Info")
    db = get_db()
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for t in tables:
        count = db.execute(f"SELECT COUNT(*) FROM {t['name']}").fetchone()[0]
        st.write(f"**{t['name']}**: {count} rows")

    if st.button("Re-initialize Seed Data", type="secondary"):
        from database.seed import seed
        seed(db)
        st.success("Seed data re-initialized.")
        st.rerun()
