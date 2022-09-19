# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('partner_id')
    def _onchange_partner_rute(self):
        for item in self:
            if item.partner_id:
                item.delivery_carrier_id = item.partner_id.property_delivery_carrier_id.id
                item.weekly_schedule_am = item.partner_id.weekly_schedule_am.ids
                item.weekly_schedule_pm = item.partner_id.weekly_schedule_pm.ids
                item.saturday_schedule_am = item.partner_id.saturday_schedule_am.ids
                item.saturday_schedule_pm = item.partner_id.saturday_schedule_pm.ids
            else:
                item.delivery_carrier_id = False
                item.weekly_schedule_am = False
                item.weekly_schedule_pm = False
                item.saturday_schedule_am = False
                item.saturday_schedule_pm = False

    def _default_activity(self):
        if self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')]):
            result = self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')], limit=1).ids
        else:
            result = False
        return result

    def _get_activity_id_domain(self):
        model = self.env['ir.model'].search([('model', '=', self._name)])
        routes = self.env['route.activity'].search([(1, '=', 1)])
        result = self.env['route.activity']
        for item in routes:
            if model.id in item.active_model_ids.ids:
                result = result + item
        return result.ids

    journal = fields.Selection([('next', 'Próxima'), ('am', 'Mañana'), ('pm', 'Tarde')], string='Jornada', required=True, default='next')
    delivery_date = fields.Datetime(string='Fecha de Entrega', default=lambda self: fields.Datetime.now())
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Metodo de Entrega')
    activity_id = fields.Many2many('route.activity', 'p_order_activity_rel', 'purchase_id', 'activity_id', string='Actividad de La Ruta', default=lambda self: self._default_activity(), domain=lambda self: [("id", "in", self._get_activity_id_domain())])
    rute_comment = fields.Text(string='Comentarios de Enrutado')
    route_id = fields.Many2one('routes', string='Enrutaje')
    weekly_schedule_am = fields.Many2many('calendar.day.megatoner', 'p_day_weekly_am_so_rel', 'purchase_order_id', 'calendar_day_id', string='Weekly Schedule Am')
    weekly_schedule_pm = fields.Many2many('calendar.day.megatoner', 'p_day_weekly_pm_so_rel', 'purchase_order_id', 'calendar_day_id', string='Weekly Schedule Am')
    saturday_schedule_am = fields.Many2many('calendar.day.megatoner', 'p_day_saturday_am_so_rel', 'purchase_order_id', 'calendar_day_id', string='Saturday Schedule AM')
    saturday_schedule_pm = fields.Many2many('calendar.day.megatoner', 'p_day_saturday_pm_so_rel', 'purchase_order_id', 'calendar_day_id', string='Saturday Schedule AM')

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        picking = self.env['stock.picking'].search([('origin', '=', self.name)])
        for item in picking:
            item.activity_id = self.activity_id.ids
            item.delivery_carrier_id = self.delivery_carrier_id.id
            item.rute_comment = self.rute_comment
            item.delivery_date = self.delivery_date
            item.journal = self.journal
            item.weekly_schedule_am = self.weekly_schedule_am.ids
            item.weekly_schedule_pm = self.weekly_schedule_pm.ids
            item.saturday_schedule_am = self.saturday_schedule_am.ids
            item.saturday_schedule_pm = self.saturday_schedule_pm.ids
        return res

    def action_generar_ruta(self):
        for item in self:
            if item.delivery_carrier_id.routes_enable and not item.route_id:
                if not item.activity_id:
                    raise ValidationError('No se puede Enrutar sin actividad Asignada')
                item.partner_id.validar_lat_long()
                route = self.env['routes'].create({
                    'delivery_carrier_id': item.delivery_carrier_id,
                    'activity_id': item.activity_id.ids if item.activity_id else False,
                    'rute_comment': item.rute_comment if item.rute_comment else False,
                    'delivery_date': item.delivery_date,
                    'street': item.partner_id.street,
                    'street2': item.partner_id.street2,
                    'city_id': item.partner_id.city_id.id,
                    'state_id': item.partner_id.state_id.id,
                    'zip_id': item.partner_id.zip_id.id,
                    'weekly_schedule_am': item.weekly_schedule_am.ids,
                    'weekly_schedule_pm': item.weekly_schedule_pm.ids,
                    'saturday_schedule_am': item.saturday_schedule_am.ids,
                    'saturday_schedule_pm': item.saturday_schedule_pm.ids,
                    'origin': 'p_order',
                    'purchase_origin_ref': item.id,
                    'partner_id': item.partner_id.id,
                    'latitude_client': item.partner_id.partner_latitude,
                    'longitude_client': item.partner_id.partner_longitude
                })
                item.route_id = route
        return True