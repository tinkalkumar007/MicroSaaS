app_name = "microsaas"
app_title = "MicroSaaS"
app_publisher = "India100x pvt. ltd."
app_description = "Handling Clients"
app_email = "ram@india100x.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "microsaas",
# 		"logo": "/assets/microsaas/logo.png",
# 		"title": "MicroSaaS",
# 		"route": "/microsaas",
# 		"has_permission": "microsaas.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/microsaas/css/microsaas.css"
# app_include_js = "/assets/microsaas/js/microsaas.js"

# include js, css files in header of web template
# web_include_css = "/assets/microsaas/css/microsaas.css"
# web_include_js = "/assets/microsaas/js/microsaas.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "microsaas/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "microsaas/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "microsaas.utils.jinja_methods",
# 	"filters": "microsaas.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "microsaas.install.before_install"
# after_install = "microsaas.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "microsaas.uninstall.before_uninstall"
# after_uninstall = "microsaas.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "microsaas.utils.before_app_install"
# after_app_install = "microsaas.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "microsaas.utils.before_app_uninstall"
# after_app_uninstall = "microsaas.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "microsaas.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"microsaas.microsaas.services.reminder_scheduler.send_invoice_reminders",
		"microsaas.microsaas.services.reminder_scheduler.check_tax_deadlines",
		"microsaas.microsaas.services.reminder_scheduler.check_document_expiry"
	],
	"hourly": [
		"microsaas.microsaas.services.reminder_scheduler.send_appointment_reminders"
	],
	"cron": {
		"0 9 * * *": [  # 9 AM daily
			"microsaas.microsaas.services.reminder_scheduler.generate_recurring_invoices"
		]
	}
}

# Testing
# -------

# before_tests = "microsaas.install.before_tests"

# Overriding Methods
# ------------------------------

override_whitelisted_methods = {
	# Payment Gateway Webhooks
	"microsaas.razorpay_webhook": "microsaas.microsaas.integrations.payment_gateway.razorpay_gateway.webhook",
	"microsaas.stripe_webhook": "microsaas.microsaas.integrations.payment_gateway.stripe_gateway.webhook",
	
	# Payment API
	"microsaas.create_payment_link": "microsaas.microsaas.api.payment_api.create_payment_link",
	"microsaas.get_invoice_payment_status": "microsaas.microsaas.api.payment_api.get_invoice_payment_status",
	"microsaas.process_manual_payment": "microsaas.microsaas.api.payment_api.process_manual_payment",
	"microsaas.refund_payment": "microsaas.microsaas.api.payment_api.refund_payment",
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "microsaas.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["microsaas.utils.before_request"]
# after_request = ["microsaas.utils.after_request"]

# Job Events
# ----------
# before_job = ["microsaas.utils.before_job"]
# after_job = ["microsaas.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"microsaas.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

