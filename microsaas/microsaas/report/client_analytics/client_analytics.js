frappe.query_reports["Client Analytics"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Firm"),
            "fieldtype": "Link",
            "options": "CA Firm",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 0
        }
    ]
};
