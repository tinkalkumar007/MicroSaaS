# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os


class CADocument(Document):
	def validate(self):
		"""Validate document data"""
		# Set file metadata
		if self.file_attachment:
			file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
			self.file_size = self.format_file_size(file_doc.file_size)
			self.file_type = file_doc.file_name.split('.')[-1].upper()
		
		# Set uploaded by
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
		

		# Set client accessible based on visibility
		if self.visibility == "Client Accessible":
			self.client_accessible = 1
		else:
			self.client_accessible = 0
			
		# Auto-set firm from client
		if self.client and not self.firm:
			self.firm = frappe.db.get_value("CA Client", self.client, "firm")
	
	def format_file_size(self, size_bytes):
		"""Format file size in human-readable format"""
		if not size_bytes:
			return "0 B"
		
		size_bytes = int(size_bytes)
		for unit in ['B', 'KB', 'MB', 'GB']:
			if size_bytes < 1024.0:
				return f"{size_bytes:.1f} {unit}"
			size_bytes /= 1024.0
		return f"{size_bytes:.1f} TB"
	
	def create_new_version(self, new_file):
		"""Create a new version of this document"""
		try:
			# Create new document as a version
			new_doc = frappe.copy_doc(self)
			new_doc.file_attachment = new_file
			new_doc.version_number = self.version_number + 1
			new_doc.previous_version = self.name
			new_doc.insert()
			
			return new_doc
			
		except Exception as e:
			frappe.log_error(f"Error creating document version: {str(e)}")
			frappe.throw("Failed to create new version")
	
	def download_document(self):
		"""Generate download link for the document"""
		if self.file_attachment:
			return frappe.utils.get_url(self.file_attachment)
		return None
