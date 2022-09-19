# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError


class PointSale(models.Model):
    _name = 'point.sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name Point', required=True)
    partner_ids = fields.One2many('res.partner', 'point_sale_id', string='Vendors', copy=False)
    session_ids = fields.One2many('pos.sale.session', 'point_sale_id', string='Session Sales', copy=False)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence of point', required=True, copy=False)

    def create_session(self, date_session=False):
        session = False
        for record in self:
            if date_session == False:
                date_session = datetime.now()
            session = self.env['pos.sale.session'].search([('point_sale_id', '=', record.id), ('start_date', '=', date_session+ ' 05:00:00')],order='name asc', limit=1)
            if not session:
                session = self.env['pos.sale.session'].create({
                    'name': record.sequence_id.next_by_id(),
                    'point_sale_id': record.id,
                    'start_date': date_session + ' 05:00:00',
                    'company_id': self.env.user.company_id.id,
                    'state': 'open',
                })
        return session