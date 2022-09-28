# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Metodo de Entrega')

    """@api.onchange('partner_id')
    def call_delivery_carrier(self):
        for item in self:
            if item.partner_id:
                if item.partner_id.with_company(self.env.user.company_id.id or 1).property_delivery_carrier_id:
                    item.delivery_carrier_id = item.partner_id.with_company(self.env.user.company_id.id or 1).property_delivery_carrier_id"""