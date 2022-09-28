# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_template(models.Model):
    """
    Overwrite to add a logic of automatic code generation
    """
    _inherit = "product.template"

    manual_template_code = fields.Boolean(string="Manual Reference",)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to trigger an additional codes generation

        Methods:
         * action_retrieve_code_parts
        """
        for val in vals_list:
            if val.get("default_code"):
                val.update({"manual_template_code": True})
        products = super(product_template, self).create(vals_list)
        if not self._context.get("no_regeneration"):
            self.action_retrieve_code_parts()
        return products

    def write(self, values):
        """
        Overwrite to trigger an additional codes generation

        Methods:
         * action_retrieve_code_parts
        """
        res = super(product_template, self).write(values)
        if not self._context.get("no_regeneration"):
            self.action_retrieve_code_parts()
        return res

    def action_retrieve_code_parts(self):
        """
        The method to re-generate variant codes

        Methods:
         * action_retrieve_code_parts of product.product
        """
        for template in self:
            template.product_variant_ids.action_retrieve_code_parts()
