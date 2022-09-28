# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_session_id = fields.Many2one('pos.sale.session', string='Session Pos', index=True)

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        for item in res:
            if not item.user_id.partner_id.point_sale_id:
                raise ValidationError('El Vendedor ' + item.user_id.name + ' no tiene un Punto de venta seleccionado \n Favor validar la informacion del dicho contacto')
            else:
                session = item.journal_id.pos_sale_id.create_session(item.invoice_date.strftime('%Y-%m-%d'))
                item.pos_session_id = session
        return res

    def cron_session(self):
        journal_ids = self.env['account.journal'].search([('pos_sale', '=', True)])
        invoice_ids = self.env['account.move'].search([('pos_session_id', '=', False),('journal_id', 'in', journal_ids.ids)],order='name asc')
        for record in invoice_ids:
            if not record.pos_session_id:
                if record.user_id.partner_id.point_sale_id:
                    session = record.journal_id.pos_sale_id.create_session(record.invoice_date.strftime('%Y-%m-%d'))
                    record.pos_session_id = session
                    session._compute_facturas()
                else:
                    raise ValidationError('El Vendedor ' + record.user_id.name + ' no tiene un Punto de venta seleccionado \n Favor validar la informacion del dicho contacto')
        sessions = self.env['pos.sale.session'].search([('state', '=', 'open')])
        for session in sessions:
            if session.start_date + timedelta(days=1) < datetime.now():
                session.state = 'close'