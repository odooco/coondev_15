# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentPos(models.Model):
    _name = 'account.payment.pos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Pagos Pos"
    _order = "date desc, name desc"
    _check_company_auto = True

    def _get_default_journal(self):
        return self.env['account.move']._search_default_journal(('bank', 'cash'))

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    move_pos_id = fields.Many2one(comodel_name='account.move.pos', string='Journal Entry', readonly=True, ondelete='cascade')
    name = fields.Char(string='Numero', copy=False, compute='_compute_name', readonly=False, store=True, index=True, tracking=True)
    is_internal_transfer = fields.Boolean(string="Transferencia Interna", readonly=False, store=True, tracking=True)
    payment_type = fields.Selection([('outbound', 'Send'), ('inbound', 'Receive'), ], string='Payment Type', default='inbound', required=True, tracking=True)
    partner_type = fields.Selection([('customer', 'Customer'),('supplier', 'Vendor'),], default='customer', tracking=True, required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer/Vendor", store=True, readonly=False, ondelete='restrict', domain="['|', ('parent_id','=', False), ('is_company','=', True)]", tracking=True)
    amount = fields.Monetary(currency_field='currency_id')
    date = fields.Date(string='Fecha')
    ref = fields.Char('Memo')
    journal_id = fields.Many2one('account.journal', string='Diario', required=True, readonly=True, states={'draft': [('readonly', False)]}, check_company=True, domain="[('type', '=', 'sale')]", default=_get_default_journal)
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Metodo de Pago', readonly=False, store=True, copy=False, domain="[('id', 'in', available_payment_method_line_ids)]", )
    partner_bank_id = fields.Many2one('res.partner.bank', string="Cuenta del Banco", readonly=False, store=True, tracking=True, domain="[('id', 'in', available_partner_bank_ids)]")
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False, compute='_compute_currency_id', help="The payment's currency.")
    company_id = fields.Many2one('res.company', 'Compañia',default=lambda s: s.env.company, required=True, index=True, states={'done': [('readonly', True)]})
