# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class Routes(models.TransientModel):
    _name = 'enrutar'

    def _get_activity_id_domain(self):
        model = self.env['ir.model'].search([('model', '=', 'res.partner')])
        routes = self.env['route.activity'].search([(1, '=', 1)])
        result = self.env['route.activity']
        for item in routes:
            if model.id in item.active_model_ids.ids:
                result = result + item
        return result.ids

    activity_id = fields.Many2many('route.activity', 'enroute_activity_rel', 'enroutes_id', 'activity_id',
                                   string='Actividad de La Ruta', default=lambda self: self._default_activity(),
                                   domain=lambda self: [("id", "in", self._get_activity_id_domain())])
    rute_comment = fields.Text(string='Comentarios de Enrutado')

    def action_generar_ruta(self):
        for item in self:
            if not self.env.context['partner_latitude']:
                raise ValidationError('El contacto ' + self.name + ' No tiene parametrizado un valor de Latitud')
            elif not self.env.context['partner_longitude']:
                raise ValidationError('El contacto ' + self.name + ' No tiene parametrizado un valor de Longitud')
            route = self.env['routes'].create({
                'activity_id': self.activity_id.ids,
                'rute_comment': self.rute_comment,
                'street': self.env.context['street'],
                'street2': self.env.context['street2'],
                'city_id': self.env.context['city_id'],
                'state_id': self.env.context['state_id'],
                'zip_id': self.env.context['zip_id'],
                'weekly_schedule_am': self.env.context['weekly_schedule_am'],
                'weekly_schedule_pm': self.env.context['weekly_schedule_pm'],
                'saturday_schedule_am': self.env.context['saturday_schedule_am'],
                'saturday_schedule_pm': self.env.context['saturday_schedule_pm'],
                'origin': 'contact',
                'partner_id': self.env.context['partner_id'],
                'delivery_carrier_id': self.env.context['delivery_carrier_id'],
                'latitude_client': self.env.context['partner_latitude'],
                'longitude_client': self.env.context['partner_longitude']
            })


class Routes(models.Model):
    _name = 'routes'
    _order = 'sequence'

    def _default_activity(self):
        if self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')]):
            result = self.env['route.activity'].search([('name', '=', 'Entregar Toner (NUEVO)')], limit=1).ids
        else:
            result = False
        return result

    sequence = fields.Integer("sequence", default=1)
    name = fields.Char(string='Nombre', )
    delivery_date = fields.Datetime(string='Fecha de Entrega', default=lambda self: fields.Datetime.now())
    journal = fields.Selection([('next', 'Próxima'), ('am', 'Mañana'), ('pm', 'Tarde')], string='Jornada',
                               required=True, default='next')
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Metodo de Entrega')
    domiciliary_id = fields.Many2one('res.partner.domiciliary', string='Domiciliario', tracking=True,
                                     group_expand='_expand_domiciliary')
    activity_id = fields.Many2many('route.activity', 'route_activity_rel', 'routes_id', 'activity_id',
                                   string='Actividad de La Ruta', default=lambda self: self._default_activity())
    rute_comment = fields.Text(string='Comentarios de Enrutado')
    state = fields.Selection(
        [('draft', 'Creada'), ('route', 'En Ruta'), ('post', 'Realizada'), ('not_post', 'No Realizada'),
         ('refuse', 'Rechazada'), ('copy', 'Duplicada'), ('cancel', 'Cancelada')], string='Estado', required=True,
        default='draft')
    street = fields.Char(string='Direccion')
    street2 = fields.Char(string='Indicaciones')
    city_id = fields.Many2one('res.city', string='Ciudad')
    state_id = fields.Many2one('res.country.state', 'Estado')
    zip_id = fields.Many2one("res.city.zip", "ZIP Location")
    latitude = fields.Float(string='Latitud Entregado', digits=(10, 7))
    longitude = fields.Float(string='Longitud Entregado', digits=(10, 7))
    weekly_schedule_am = fields.Many2many('calendar.day.megatoner', 'r_day_weekly_am_rel', 'routes_id',
                                          'calendar_day_id', string='Weekly Schedule Am')
    weekly_schedule_pm = fields.Many2many('calendar.day.megatoner', 'r_day_weekly_pm_rel', 'routes_id',
                                          'calendar_day_id', string='Weekly Schedule Am')
    saturday_schedule_am = fields.Many2many('calendar.day.megatoner', 'r_day_saturday_am_rel', 'routes_id',
                                            'calendar_day_id', string='Saturday Schedule AM')
    saturday_schedule_pm = fields.Many2many('calendar.day.megatoner', 'r_day_saturday_pm_rel', 'routes_id',
                                            'calendar_day_id', string='Saturday Schedule AM')
    origin = fields.Selection(
        [('manual', 'Rutas'), ('s_order', 'Orden de Venta'), ('p_order', 'Orden de Compra'), ('contact', 'Contacto'),
         ('ticket', 'Ticket'), ('piking', 'Entrega'), ('invoice', 'Factura')], string='Origen')
    sale_origin_ref = fields.Many2one("sale.order", "Nro Venta de Origen")
    invoice_origin_ref = fields.Many2one("account.move", "Nro Factura de Origen")
    purchase_origin_ref = fields.Many2one("purchase.order", "Nro Compra de Origen")
    ticket_origin_ref = fields.Many2one("helpdesk.ticket", "Nro Ticket Origen")
    delivery_origin_ref = fields.Many2one("stock.picking", "Nro Transferencia Origen")
    partner_id = fields.Many2one('res.partner', string='Cliente')
    latitude_client = fields.Float(string='Latitud Cliente', digits=(10, 7))
    longitude_client = fields.Float(string='Longitud Cliente', digits=(10, 7))
    register_date = fields.Datetime('Fecha y Hora Registro', default=lambda self: fields.Datetime.now())

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

    def _expand_domiciliary(self, domiciliary_id, domain, order):
        domiciliary_id = self.env['res.partner.domiciliary'].search([])
        return domiciliary_id

    @api.model
    def create(self, vals):
        result = super(Routes, self).create(vals)
        result.name = 'Ruta # ' + str(result.id)
        return result


class MapsRoutes(models.TransientModel):
    _name = "maps.routes"

    domiciliary_ids = fields.Many2many('res.partner.domiciliary', 'partner_domiciliary_id', 'maps_id', string='Domiciliarios', tracking=True)
    delivery_date = fields.Datetime(string='Fecha inicial de Entrega', default=lambda self: fields.Datetime.now())
    delivery_date_due = fields.Datetime(string='Fecha final de Entrega', default=lambda self: fields.Datetime.now() + relativedelta(days=1))

    def action_generar_rutas(self):
        frm_address = ''
        domiciliary_address = ''
        company = self.env.user.company_id
        if company.street:
            frm_address += company.street.replace(' ', '+')
        if company.street2:
            frm_address += (' ')
            frm_address += company.street2.replace(' ', '+')
        if company.city:
            frm_address += (' ')
            frm_address += company.city.replace(' ', '+')
        if company.state_id:
            frm_address += (' ')
            frm_address += company.state_id.name.replace(' ', '+')
        if company.zip:
            frm_address += (' ')
            frm_address += company.zip.replace(' ', '+')
        if company.country_id:
            frm_address += (' ')
            frm_address += company.country_id.name.replace(' ', '+')
        for domiciliary_id in self.domiciliary_ids:
            routes_ids = self.env['routes'].search(
                [('domiciliary_id', '=', domiciliary_id.id), ('delivery_date', '>=', self.delivery_date),
                 ('delivery_date', '<=', self.delivery_date_due)])
            for item in routes_ids:
                to_address = ''
                if item.partner_id.street:
                    to_address += item.partner_id.street.replace(' ', '+')
                if item.partner_id.street2:
                    to_address += (' ')
                    to_address += item.partner_id.street2.replace(' ', '+')
                if item.partner_id.city_id:
                    to_address += (' ')
                    to_address += item.partner_id.city_id.name.replace(' ', '+')
                if item.partner_id.state_id:
                    to_address += (' ')
                    to_address += item.partner_id.state_id.name.replace(' ', '+')
                if item.partner_id.zip_id:
                    to_address += (' ')
                    to_address += item.partner_id.zip_id.name.replace(' ', '+')
                if item.partner_id.country_id:
                    to_address += (' ')
                    to_address += item.partner_id.country_id.name.replace(' ', '+')
                domiciliary_address += to_address + '/'
            domiciliary_address += frm_address + '/'

        url = "https://www.google.co.in/maps/dir/{}/{}".format(frm_address, domiciliary_address)
        return {
            'name': ("map_route"),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    """
    def action_generar_rutas(self):
        frm_address = ''
        domiciliary_address = ''
        company = self.env.user.company_id
        if company.partner_id:
            frm_address += str(company.partner_id.partner_latitude).replace(',', '.')+','+str(company.partner_id.partner_longitude).replace(',', '.')
        for domiciliary_id in self.domiciliary_ids:
            routes_ids = self.env['routes'].search([('domiciliary_id', '=', domiciliary_id.id), ('delivery_date', '>=', self.delivery_date),('delivery_date', '<=', self.delivery_date_due)])
            for item in routes_ids:
                domiciliary_address += str(item.latitude_client).replace(',', '.')+','+str(item.longitude_client).replace(',', '.')+'/'
            domiciliary_address += frm_address + '/'

        url = "https://www.google.co.in/maps/dir/{}/{}".format(frm_address, domiciliary_address)
        return {
            'name': ("map_route"),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    """