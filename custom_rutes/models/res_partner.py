# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    route_id = fields.Many2one('routes', string='Enrutaje')
    route_state = fields.Boolean(related='property_delivery_carrier_id.routes_enable', string='Enruta?')

    def _default_activity(self):
        if self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')]):
            result = self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')], limit=1).ids
        else:
            result = False
        return result

    def validar_lat_long(self):
        for item in self:
            if not item.partner_latitude:
                raise ValidationError('El contacto '+self.name+' No tiene parametrizado un valor de Latitud')
            elif not item.partner_longitude:
                raise ValidationError('El contacto '+self.name+' No tiene parametrizado un valor de Longitud')

    def action_generar_ruta(self):
        for item in self:
            item.validar_lat_long()
            route = self.env['routes'].create({
                'delivery_carrier_id': item.property_delivery_carrier_id.id,
                'street': item.street,
                'street2': item.street2,
                'city_id': item.city_id.id or False,
                'state_id': item.state_id.id or False,
                'zip_id': item.zip_id.id or False,
                'weekly_schedule_am': item.weekly_schedule_am.ids or False,
                'weekly_schedule_pm': item.weekly_schedule_pm.ids or False,
                'saturday_schedule_am': item.saturday_schedule_am.ids or False,
                'saturday_schedule_pm': item.saturday_schedule_pm.ids or False,
                'origin': 'contact',
                'partner_id': item.id,
                'latitude_client': item.partner_latitude,
                'longitude_client': item.partner_longitude
            })

    def cargar_ruta(self):
        return {
            'name': 'Generar Ruta de Contacto',
            'domain': [],
            'res_model': 'enrutar',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_activity_id': self._default_activity(),
                'route_id': self.route_id,
                'street': self.street,
                'street2': self.street2,
                'city_id': self.city_id.id or False,
                'state_id': self.state_id.id or False,
                'zip_id': self.zip_id.id or False,
                'weekly_schedule_am': self.weekly_schedule_am.ids or False,
                'weekly_schedule_pm': self.weekly_schedule_pm.ids or False,
                'saturday_schedule_am': self.saturday_schedule_am.ids or False,
                'saturday_schedule_pm': self.saturday_schedule_pm.ids or False,
                'partner_id': self.id,
                'delivery_carrier_id': self.property_delivery_carrier_id.id,
                'partner_latitude': self.partner_latitude,
                'partner_longitude': self.partner_longitude,
            },
            'target': 'new',
        }