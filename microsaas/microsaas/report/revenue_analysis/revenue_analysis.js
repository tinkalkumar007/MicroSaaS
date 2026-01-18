frappe.query_reports["Revenue Analysis"] = {
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
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ]
};
