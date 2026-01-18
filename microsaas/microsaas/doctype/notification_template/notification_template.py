# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from jinja2 import Template


class NotificationTemplate(Document):
	def validate(self):
		"""Validate template content"""
		# Test template rendering with preview data
		if self.preview_data:
			try:
				preview_dict = json.loads(self.preview_data)
				self.preview_output = self.render(preview_dict)
			except Exception as e:
				frappe.msgprint(f"Error rendering template: {str(e)}")
	
	def render(self, data):
		"""Render template with provided data"""
		try:
			template = Template(self.template_content)
			return template.render(**data)
		except Exception as e:
			frappe.log_error(f"Template rendering error: {str(e)}")
			return None
