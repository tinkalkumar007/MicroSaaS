
import frappe
import json
import os

def setup_rbac():
    create_roles()
    update_doctype_permissions()

def create_roles():
    roles = ["CA Firm Admin", "CA Staff", "CA Client User"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1
            }).insert(ignore_permissions=True)
            print(f"Created Role: {role}")
        else:
            print(f"Role already exists: {role}")

def update_doctype_permissions():
    app_path = frappe.get_app_path("microsaas")
    
    # Define permissions
    admin_perms = {
        "role": "CA Firm Admin",
        "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1, 
        "report": 1, "export": 1, "import": 1, "share": 1, "print": 1, "email": 1
    }
    
    staff_perms = {
        "role": "CA Staff",
        "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0, "amend": 1,
        "report": 1, "export": 1, "print": 1, "email": 1
    }
    
    client_perms = {
        "role": "CA Client User",
        "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, 
        "print": 1, "email": 1, "report": 0
    }

    # DocType configurations
    doctypes = {
        "CA Client": [admin_perms, staff_perms],
        "CA Invoice": [admin_perms, staff_perms, client_perms],
        "CA Payment": [admin_perms, staff_perms, client_perms],
        "CA Appointment": [admin_perms, staff_perms, client_perms], # Client helper logic might allow create
        "CA Document": [admin_perms, staff_perms, client_perms],
        "CA Firm": [admin_perms], # Only Admin
        "CA Settings": [admin_perms] # Only Admin
    }

    for dt, perms in doctypes.items():
        # folder name is usually snake_case of doctype
        dt_folder = frappe.scrub(dt)
        file_path = os.path.join(app_path, "microsaas", "doctype", dt_folder, f"{dt_folder}.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Filter out existing System Manager perm to keep, or just append?
            # Let's keep existing and append new ones if not present
            existing_roles = [p.get("role") for p in data.get("permissions", [])]
            
            for p in perms:
                if p["role"] not in existing_roles:
                    data["permissions"].append(p)
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=1) # 1 tab indent? Frappe uses tab or 1 space? usually 1 space or tab. 
                # checking previous file read, it was 4 spaces or tab. 
                # Standard frappe is 1 tab. Python json doesn't support tab indent easily, but indent=1 with custom encoder?
                # Actually commonly used indent=1 is 1 space.
                # Let's stick to indent=1 for now.
            
            print(f"Updated permissions for {dt}")
        else:
            print(f"File not found: {file_path}")

