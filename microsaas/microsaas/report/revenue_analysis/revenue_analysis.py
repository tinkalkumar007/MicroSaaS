
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{
			"fieldname": "period",
			"label": _("Period"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "service_type",
			"label": _("Service Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "invoice_count",
			"label": _("Invoices"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	# Fetch invoices
	data = frappe.db.sql(f"""
		SELECT
			DATE_FORMAT(invoice_date, '%%Y-%%m') as period,
			DATE_FORMAT(invoice_date, '%%M %%Y') as period_label,
            # We need to join with Items or just use Description? 
            # CA Invoice has items child table but maybe we categorize by Client Service Type?
            # Let's assume we want revenue by time first.
            # If we want by service type, we need to join CA Invoice Item.
            # Let's stick to simple monthly revenue for now, or fetch items if needed.
            # actually let's try to get service type from Client? No, Invoice Item is better.
			count(name) as invoice_count,
			sum(total_amount) as revenue
		FROM
			`tabCA Invoice`
		WHERE
			docstatus = 1 {conditions}
		GROUP BY
			period
		ORDER BY
			period desc
	""", filters, as_dict=1)
    
    # Post-process for better labeling if needed
	result = []
	for row in data:
		result.append({
			"period": row.period_label,
			"service_type": "All Services", # placeholder until we detail by item
			"invoice_count": row.invoice_count,
			"revenue": row.revenue,
			"currency": filters.get("currency") or "INR"
		})
		
	return result

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND firm = %(company)s"
	
	if filters.get("from_date"):
		conditions += " AND invoice_date >= %(from_date)s"
		
	if filters.get("to_date"):
		conditions += " AND invoice_date <= %(to_date)s"
		
	return conditions

def get_chart(data):
	if not data:
		return None
		
	labels = [d.get("period") for d in data]
	values = [d.get("revenue") for d in data]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Revenue",
					"values": values
				}
			]
		},
		"type": "bar"
	}
