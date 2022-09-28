# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    journal = fields.Selection([('next', 'Próxima'), ('am', 'Mañana'), ('pm', 'Tarde')], string='Jornada', required=True, default='next')
    activity_id = fields.Many2many('route.activity', 's_order_activity_rel', 'sale_id', 'activity_id', string='Actividad de La Ruta', default=lambda self: self._default_activity(), domain=lambda self: [("id", "in", self._get_activity_id_domain())])
    delivery_date = fields.Datetime(string='Fecha de Entrega', default=lambda self: fields.Datetime.now())
    rute_comment = fields.Text(string='Comentarios de Enrutado')
    route_id = fields.Many2one('routes', string='Enrutaje')
    weekly_schedule_am = fields.Many2many('calendar.day.megatoner', 'c_day_weekly_am_so_rel', 'sale_order_id',
                                          'calendar_day_id', string='Weekly Schedule Am')
    weekly_schedule_pm = fields.Many2many('calendar.day.megatoner', 'c_day_weekly_pm_so_rel', 'sale_order_id',
                                          'calendar_day_id', string='Weekly Schedule Am')
    saturday_schedule_am = fields.Many2many('calendar.day.megatoner', 'c_day_saturday_am_so_rel', 'sale_order_id',
                                            'calendar_day_id', string='Saturday Schedule AM')
    saturday_schedule_pm = fields.Many2many('calendar.day.megatoner', 'c_day_saturday_pm_so_rel', 'sale_order_id',
                                            'calendar_day_id', string='Saturday Schedule AM')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        picking = self.env['stock.picking'].search([('sale_id', '=', self.id)])
        for item in picking:
            item.activity_id = self.activity_id
            item.delivery_carrier_id = self.delivery_carrier_id
            item.delivery_date = self.delivery_date
            item.rute_comment = self.rute_comment
            item.journal = self.journal
            item.weekly_schedule_am = self.weekly_schedule_am
            item.weekly_schedule_pm = self.weekly_schedule_pm
            item.saturday_schedule_am = self.saturday_schedule_am
            item.saturday_schedule_pm = self.saturday_schedule_pm
        return res

    def action_generar_ruta(self):
        for item in self:
            if item.delivery_carrier_id.routes_enable and not item.route_id:
                if not item.activity_id:
                    raise ValidationError('No se puede Enrutar sin actividad Asignada')
                if item.partner_shipping_id:
                    item.partner_shipping_id.validar_lat_long()
                    route = self.env['routes'].create({
                        'journal': item.journal,
                        'activity_id': item.activity_id.ids if item.activity_id else False,
                        'delivery_date': item.delivery_date,
                        'rute_comment': item.rute_comment if item.rute_comment else False,
                        'delivery_carrier_id': item.delivery_carrier_id.id if item.delivery_carrier_id else False,
                        'street': item.partner_shipping_id.street,
                        'street2': item.partner_shipping_id.street2,
                        'city_id': item.partner_shipping_id.city_id.id if item.partner_shipping_id.city_id else False,
                        'state_id': item.partner_shipping_id.state_id.id if item.partner_shipping_id.state_id else False,
                        'zip_id': item.partner_shipping_id.zip_id.id if item.partner_shipping_id.zip_id else False,
                        'origin': 's_order',
                        'sale_origin_ref': item.id,
                        'partner_id': item.partner_id.id or False,
                        'latitude_client': item.partner_shipping_id.partner_latitude,
                        'longitude_client': item.partner_shipping_id.partner_longitude
                    })
                    route.weekly_schedule_am = item.partner_id.weekly_schedule_am or False
                    route.weekly_schedule_pm = item.partner_id.weekly_schedule_pm or False
                    route.saturday_schedule_am = item.partner_id.saturday_schedule_am or False
                    route.saturday_schedule_pm = item.partner_id.saturday_schedule_pm or False
                elif item.partner_id:
                    item.partner_id.validar_lat_long()
                    route = self.env['routes'].create({
                        'journal': item.journal,
                        'activity_id': item.activity_id.ids or False,
                        'rute_comment': item.rute_comment or False,
                        'delivery_date': item.delivery_date,
                        'delivery_carrier_id': item.delivery_carrier_id.id if item.delivery_carrier_id else False,
                        'street': item.partner_id.street,
                        'street2': item.partner_id.street2,
                        'city_id': item.partner_id.city_id.id or False,
                        'state_id': item.partner_id.state_id.id or False,
                        'zip_id': item.partner_id.zip_id.id or False,
                        'origin': 's_order',
                        'sale_origin_ref': item.id,
                        'partner_id': item.partner_id.id or False,
                        'latitude_client': item.partner_id.partner_latitude,
                        'longitude_client': item.partner_id.partner_longitude
                    })
                    route.weekly_schedule_am = item.partner_shipping_id.weekly_schedule_am or False
                    route.weekly_schedule_pm = item.partner_shipping_id.weekly_schedule_pm or False
                    route.saturday_schedule_am = item.partner_shipping_id.saturday_schedule_am or False
                    route.saturday_schedule_pm = item.partner_shipping_id.saturday_schedule_pm or False
                else:
                    raise ValidationError('Asigune un contacto valido para Continuar')
                item.route_id = route
        return True

    @api.onchange('weekly_schedule_am', 'weekly_schedule_pm', 'saturday_schedule_am', 'saturday_schedule_pm')
    def _onchange_weekly_schedule(self):
        for item in self:
            if len(item.weekly_schedule_am) > 2:
                raise ValidationError('Defina solamente 2 horas para el horario semanal en la mañana')
            if len(item.weekly_schedule_pm) > 2:
                raise ValidationError('Defina solamente 2 horas para el horario semanal en la tarde')
            if len(item.saturday_schedule_am) > 2:
                raise ValidationError('Defina solamente 2 horas para el horario sabatino en la mañana')
            if len(item.saturday_schedule_pm) > 2:
                raise ValidationError('Defina solamente 2 horas para el horario sabatino en la tarde')