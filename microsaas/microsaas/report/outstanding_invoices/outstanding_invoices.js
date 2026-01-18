frappe.query_reports["Outstanding Invoices"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Firm"),
            "fieldtype": "Link",
            "options": "CA Firm",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 0
        },
        {
            "fieldname": "client",
            "label": __("Client"),
            "fieldtype": "Link",
            "options": "CA Client",
            "reqd": 0
        }
    ]
};
