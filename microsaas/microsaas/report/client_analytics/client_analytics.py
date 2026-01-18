
import frappe
from frappe import _

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
			"fieldname": "total_invoiced",
			"label": _("Total Invoiced"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "total_paid",
			"label": _("Total Paid"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "outstanding",
			"label": _("Outstanding"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "last_invoice_date",
			"label": _("Last Invoice"),
			"fieldtype": "Date",
			"width": 100
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
	
	# Fetch aggregated data
	data = frappe.db.sql(f"""
		SELECT
			client,
			SUM(total_amount) as total_invoiced,
			MAX(invoice_date) as last_invoice_date,
			firm,
			currency
		FROM
			`tabCA Invoice`
		WHERE
			docstatus = 1 {conditions}
		GROUP BY
			client
	""", filters, as_dict=1)
	
	result = []
	for row in data:
		# Calculate paid amount
		paid_amount = frappe.db.sql("""
			SELECT SUM(amount) 
			FROM `tabCA Payment` 
			WHERE client = %s AND status = 'Completed' AND docstatus = 1
		""", row.client)[0][0] or 0
		
		row["total_paid"] = paid_amount
		row["outstanding"] = row["total_invoiced"] - paid_amount
		
		if row["outstanding"] > 0:
			row["status"] = "Pending"
		else:
			row["status"] = "Clear"
			
		result.append(row)
		
	return result

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND firm = %(company)s"
		
	return conditions
