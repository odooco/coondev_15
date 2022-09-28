# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval

class ResConfigSettingsInherit(models.TransientModel):
	_inherit = "res.config.settings"
	_description = "Res Config Settings"

	def get_fields_domain(self):
		objs = self.env['ir.model'].search([("model","=","res.partner")]);
		return "[('store','=',True),('ttype','in',['text','char']),('model_id','in',%s)]"%(objs.ids);

	fields_ids = fields.Many2many("ir.model.fields",string="Fields To Check", domain=get_fields_domain);

	@api.model
	def get_values(self):
		res = super(ResConfigSettingsInherit, self).get_values()
		fields_ids = self.env["ir.config_parameter"].sudo().get_param("bi_duplicate_field_validation.fields_ids");
		res.update(
		    fields_ids = [(6,0,literal_eval(fields_ids))] if fields_ids else False,
			)
		return res

	def set_values(self):
		res = super(ResConfigSettingsInherit, self).set_values();
		self.env["ir.config_parameter"].sudo().set_param("bi_duplicate_field_validation.fields_ids", self.fields_ids.ids);
		return res;


	




