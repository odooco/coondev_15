# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    routes_enable = fields.Boolean(string='Enruta?', default=True)