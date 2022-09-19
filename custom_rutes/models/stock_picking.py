# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _default_activity(self):
        if self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')]):
            result = self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')], limit=1).ids
        else:
            result = False
        return result

    def _get_activity_id_domain(self):
        model = self.env['ir.model'].search([('model','=',self._name)])
        routes = self.env['route.activity'].search([(1,'=',1)])
        result = []
        for item in routes:
            if model.id in item.active_model_ids.ids:
                result.append(item)
        return result

    def _get_activity_id_domain(self):
        model = self.env['ir.model'].search([('model', '=', self._name)])
        routes = self.env['route.activity'].search([(1, '=', 1)])
        result = self.env['route.activity']
        for item in routes:
            if model.id in item.active_model_ids.ids:
                result = result + item
        return result.ids

    journal = fields.Selection([('next', 'Próxima'), ('am', 'Mañana'), ('pm', 'Tarde')], string='Jornada', default='next')
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Metodo de Entrega')
    delivery_date = fields.Datetime(string='Fecha de Entrega', default=lambda self: fields.Datetime.now())
    activity_id = fields.Many2many('route.activity', 'picking_activity_rel', 'picking_id', 'activity_id', string='Actividad de La Ruta', default=lambda self: self._default_activity(), domain=lambda self: [("id", "in", self._get_activity_id_domain())])
    rute_comment = fields.Text(string='Comentarios de Enrutado')
    route_state = fields.Boolean(related='delivery_carrier_id.routes_enable', string='Enruta?')
    route_id = fields.Many2one('routes', string='Enrutaje')
    weekly_schedule_am = fields.Many2many('calendar.day.megatoner', 's_day_weekly_am_so_rel', 'picking_order_id', 'calendar_day_id', string='Weekly Schedule Am')
    weekly_schedule_pm = fields.Many2many('calendar.day.megatoner', 's_day_weekly_pm_so_rel', 'picking_order_id', 'calendar_day_id', string='Weekly Schedule Am')
    saturday_schedule_am = fields.Many2many('calendar.day.megatoner', 's_day_saturday_am_so_rel', 'picking_order_id', 'calendar_day_id', string='Saturday Schedule AM')
    saturday_schedule_pm = fields.Many2many('calendar.day.megatoner', 's_day_saturday_pm_so_rel', 'picking_order_id', 'calendar_day_id', string='Saturday Schedule AM')

    @api.model
    def create(self, vals):
        rec = super(StockPicking, self).create(vals)
        if rec.origin:
            if rec.sale_id:
                origin = self.sale_id
            else:
                origin = self.env['purchase.order'].search([('name','=',rec.origin)], limit=1)
            rec.delivery_carrier_id = origin.delivery_carrier_id
            rec.activity_id = origin.activity_id.ids
            rec.journal = origin.journal
            rec.delivery_date = origin.delivery_date
            rec.weekly_schedule_am = origin.weekly_schedule_am
            rec.weekly_schedule_pm = origin.weekly_schedule_pm
            rec.saturday_schedule_am = origin.saturday_schedule_am
            rec.saturday_schedule_pm = origin.saturday_schedule_pm
            rec.rute_comment = origin.rute_comment
        return rec

    def action_generar_ruta(self):
        for item in self:
            if item.delivery_carrier_id.routes_enable and not item.route_id:
                if not item.activity_id:
                    raise ValidationError('No se puede Enrutar sin actividad Asignada')
                item.partner_id.validar_lat_long()
                route = self.env['routes'].create({
                    'delivery_carrier_id': item.delivery_carrier_id.id if item.sale_id and item.sale_id.delivery_carrier_id else False,
                    'activity_id': item.activity_id.ids if item.activity_id else False,
                    'rute_comment': item.rute_comment,
                    'journal': item.journal,
                    'delivery_date': item.delivery_date,
                    'street': item.partner_id.street,
                    'street2': item.partner_id.street2,
                    'city_id': item.partner_id.city_id.id,
                    'state_id': item.partner_id.state_id.id,
                    'zip_id': item.partner_id.zip_id.id,
                    'weekly_schedule_am': item.weekly_schedule_am.ids if item.weekly_schedule_am else item.partner_id.weekly_schedule_am.ids,
                    'weekly_schedule_pm': item.weekly_schedule_pm.ids if item.weekly_schedule_pm else item.partner_id.weekly_schedule_pm.ids,
                    'saturday_schedule_am': item.saturday_schedule_am.ids if item.saturday_schedule_am.ids else item.partner_id.saturday_schedule_am.ids,
                    'saturday_schedule_pm': item.saturday_schedule_pm.ids if item.saturday_schedule_pm.ids else item.partner_id.saturday_schedule_pm.ids,
                    'origin': 'piking',
                    'sale_origin_ref': item.sale_id.id,
                    'purchase_origin_ref': self.env['purchase.order'].search([('name','=',item.origin)]).id or False,
                    'delivery_origin_ref': item.id,
                    'partner_id': item.partner_id.id,
                    'latitude_client': item.partner_id.partner_latitude,
                    'longitude_client': item.partner_id.partner_longitude
                })
                item.sale_id.route_id = route
                purchase = self.env['purchase.order'].search([('name','=',item.origin)], limit=1)
                if purchase:
                    purchase.route_id = route
                item.route_id = route
        return True

    @api.onchange('partner_id')
    def _onchange_partner_rute(self):
        for item in self:
            if item.partner_id:
                item.delivery_carrier_id = item.partner_id.property_delivery_carrier_id.id
            else:
                item.delivery_carrier_id = False

