# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
	_inherit = "res.partner"
	_description = "Res Partner"


	def get_all_validation_fields(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		fields = {};
		field = self.env["ir.model.fields"];
		if setting["fields_ids"]:
			for rec_id in setting["fields_ids"][0][2]:
				f = field.browse(rec_id)
				fields.update({f.name : f.field_description});
		return fields

	def get_records_with_case(self,field_name,field_content):
		self._cr.execute("""
			SELECT id,%s,company_id FROM res_partner
			"""%(field_name));
		recs = [];
		for i in self._cr.fetchall():
			if i[1]:
				if i[1].lower() == field_content.lower():
					recs.append(i[0]);
		records = self.env["res.partner"].sudo().browse(recs);
		return records;


	def check_duplicate_value(self,field_name,field_content,company):
		if field_content:
			records = self.get_records_with_case(field_name,field_content);
			if records:
				records = records.filtered(lambda s: s.company_id.id == company);
				if records:
					return True;
		return False;


	@api.model
	def create(self,vals):
		fields = self.get_all_validation_fields();
		if "company_id" in vals:
			company = vals["company_id"];
		else:
			company = False;
		read_list = self.sudo().read();
		for name in fields.keys():
			if name in vals:
				if self.check_duplicate_value(name, vals[name],company):
					self.popup_error(fields[name]);
			else:
				if len(read_list):
					if self.check_duplicate_value(name, self.read()[0][name],company):
						self.popup_error(fields[name]);
		return super(ResPartnerInherit, self).create(vals);

	def write(self,vals):
		for item in self:
			fields = item.get_all_validation_fields();
			if "company_id" in vals:
				company = vals["company_id"];
			else:
				company = item.company_id.id;
			data = self.sudo().read();
			if len(data):
				data =data[0];
			for name in fields.keys():
				if "company_id" in vals:
					if data[name]:
						if self.env["res.partner"].search([(name,"=",data[name]),("company_id","=",vals["company_id"])]):
							item.popup_error(fields[name]);
				if name in vals:
					if data[name] != vals[name]:
						if item.check_duplicate_value(name, vals[name],company):
							item.popup_error(fields[name]);
		return super(ResPartnerInherit, self).write(vals);


	def popup_error(self,name):
		error_msg = name + " should not be same.\nPlease enter unique " + name;
		raise ValidationError(_(error_msg));




	




