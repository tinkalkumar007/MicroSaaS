
import frappe
from frappe import _
from frappe.utils import today, date_diff

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "client",
			"label": _("Client"),
			"fieldtype": "Link",
			"options": "CA Client",
			"width": 180
		},
		{
			"fieldname": "invoice_number",
			"label": _("Invoice"),
			"fieldtype": "Link",
			"options": "CA Invoice",
			"width": 140
		},
		{
			"fieldname": "invoice_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "due_date",
			"label": _("Due Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "age",
			"label": _("Age (Days)"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "total_amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			name as invoice_number,
			client,
			invoice_date,
			due_date,
			total_amount,
			status,
			currency
		FROM
			`tabCA Invoice`
		WHERE
			docstatus = 1 
			AND status IN ('Unpaid', 'Partially Paid', 'Overdue')
			{conditions}
		ORDER BY
			due_date asc
	""", filters, as_dict=1)
	
	result = []
	for row in data:
		age = date_diff(today(), row.due_date) if row.due_date else 0
		row["age"] = max(0, age) # Show 0 if not yet due? Or negative? Let's show actual age relative to due date.
        # Actually positive age means overdue.
		if age > 0:
			row["status"] = "Overdue" # Force status if calc matches
			
		result.append(row)
		
	return result

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND firm = %(company)s"
		
	if filters.get("client"):
		conditions += " AND client = %(client)s"
		
	return conditions
