# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    eom_reference = fields.Char(string='Reference OEM')
    manufacturer_reference = fields.Char(string='Manufacturer Reference')
    product_brand_id = fields.Many2many('product.brand.megatoner','product_brand_product_template_rel','tmpl_id','brand_id', string='Brand', index=True)
    product_color_id = fields.Many2one('product.color.megatoner', string='Color', index=True)
    performance_ref = fields.Text(string='Performance')
    compatibility_ref = fields.Text(string='Compatibility')
    automatic_code = fields.Boolean(string='Codigo Automatico', default=True)

    @api.onchange('categ_id','automatic_code')
    def calculate_category_code(self):
        for item in self:
            if item.automatic_code:
                if item.categ_id and item.categ_id.category_code:
                    code_sequence = str(item.categ_id.sequence_code)
                    while len(code_sequence)<3:
                        code_sequence='0'+code_sequence
                    item.default_code = item.categ_id.category_code+code_sequence

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if vals.get('categ_id'):
            res.categ_id.next_code()
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if vals.get('categ_id'):
            self.categ_id.next_code()
        return res