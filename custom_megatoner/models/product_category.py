# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class ProductCategoryCode(models.Model):
    _inherit = 'product.category'

    sequence_code = fields.Integer(string='Secuencia de Productos', copy=False, default=1)

    def next_code(self):
        for item in self:
            item.sequence_code = item.sequence_code+1