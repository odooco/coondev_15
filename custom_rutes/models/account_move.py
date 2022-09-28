# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class AccountMove(models.Model):
    _inherit = "account.move"

    route_id = fields.Many2one('routes', string='Enrutaje')

    def action_generar_ruta(self):
        for item in self:
            if item.partner_shipping_id:
                item.partner_shipping_id.validar_lat_long()
                route = self.env['routes'].create({
                    'delivery_carrier_id': False,
                    'street': item.partner_shipping_id.street,
                    'street2': item.partner_shipping_id.street2,
                    'city_id': item.partner_shipping_id.city_id.id,
                    'state_id': item.partner_shipping_id.state_id.id,
                    'zip_id': item.partner_shipping_id.zip_id.id,
                    'weekly_schedule_am': item.partner_shipping_id.weekly_schedule_am.ids,
                    'weekly_schedule_pm': item.partner_shipping_id.weekly_schedule_pm.ids,
                    'saturday_schedule_am': item.partner_shipping_id.saturday_schedule_am.ids,
                    'saturday_schedule_pm': item.partner_shipping_id.saturday_schedule_pm.ids,
                    'origin': 'invoice',
                    'invoice_origin_ref': item.id,
                    'partner_id': item.partner_id.id,
                    'latitude_client': item.partner_shipping_id.partner_latitude,
                    'longitude_client': item.partner_shipping_id.partner_longitude
                })
            else:
                item.partner_id.validar_lat_long()
                route = self.env['routes'].create({
                    'delivery_carrier_id': False,
                    'street': item.partner_id.street,
                    'street2': item.partner_id.street2,
                    'city_id': item.partner_id.city_id.id,
                    'state_id': item.partner_id.state_id.id,
                    'zip_id': item.partner_id.zip_id.id,
                    'weekly_schedule_am': item.partner_id.weekly_schedule_am.ids,
                    'weekly_schedule_pm': item.partner_id.weekly_schedule_pm.ids,
                    'saturday_schedule_am': item.partner_id.saturday_schedule_am.ids,
                    'saturday_schedule_pm': item.partner_id.saturday_schedule_pm.ids,
                    'origin': 'invoice',
                    'invoice_origin_ref': item.id,
                    'partner_id': item.partner_id.id,
                    'latitude_client': item.partner_id.partner_latitude,
                    'longitude_client': item.partner_id.partner_longitude
                })
            item.route_id = route
        return True