# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID


class ResPartner(models.Model):
    _inherit = 'res.partner'

    point_sale_id = fields.Many2one('point.sale', string='Point of Sale', index=True)