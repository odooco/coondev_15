# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict

class AccountPaymentPosRegister(models.TransientModel):
    _name = 'account.payment.pos.register'
    _description = 'Register Payment Pos'

    def _get_default_journal(self):
        return self.env['account.move']._search_default_journal(('bank', 'cash'))

    @api.depends('partner_id', 'company_id', 'payment_type', 'is_internal_transfer')
    def _compute_available_partner_bank_ids(self):
        for pay in self:
            if pay.payment_type == 'inbound':
                pay.available_partner_bank_ids = pay.journal_id.bank_account_id
            elif pay.is_internal_transfer:
                pay.available_partner_bank_ids = pay.journal_id.bank_account_id
            else:
                pay.available_partner_bank_ids = pay.partner_id.bank_ids.filtered(
                    lambda x: x.company_id.id in (False, pay.company_id.id))._origin

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    def _get_payment_method_codes_to_exclude(self):
        self.ensure_one()
        return []

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                    lambda x: x.code not in to_exclude)
    state = fields.Selection(selection=[('draft', 'Borrador'), ('posted', 'Publicado'), ('cancel', 'Cancelado')],
                             string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    move_pos_id = fields.Many2one(comodel_name='account.move.pos', string='Factura', readonly=True,
                                  ondelete='cascade')
    name = fields.Char(string='Numero', copy=False, compute='_compute_name', readonly=False, store=True, index=True,
                       tracking=True)
    is_internal_transfer = fields.Boolean(string="Transferencia Interna", readonly=False, store=True, tracking=True)
    payment_type = fields.Selection([('outbound', 'Enviada'), ('inbound', 'Recibido'), ], string='Payment Type',
                                    default='inbound', required=True, tracking=True)
    partner_type = fields.Selection([('customer', 'Cliente'), ('supplier', 'Vendedor'), ], default='customer',
                                    tracking=True, required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Cliente", store=True, readonly=False,
                                 ondelete='restrict',
                                 domain="['|', ('parent_id','=', False), ('is_company','=', True)]", tracking=True)
    amount = fields.Monetary(currency_field='currency_id')
    payment_date = fields.Date(string='Fecha')
    communication = fields.Char('Referencia / Memo')
    journal_id = fields.Many2one('account.journal', string='Diario', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="[('type', '=', 'sale')]", default=_get_default_journal)
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Metodo de Pago', readonly=False,
                                             store=True, copy=False, domain="[('id', '!=', 0)]")
    available_partner_bank_ids = fields.Many2many(comodel_name='res.partner.bank',
                                                  compute='_compute_available_partner_bank_ids')
    partner_bank_id = fields.Many2one('res.partner.bank', string="Cuenta del Banco", readonly=False, store=True,
                                      tracking=True, domain="[('id', 'in', available_partner_bank_ids)]")
    currency_id = fields.Many2one('res.currency', string='Moneda', store=True, readonly=False,
                                  compute='_compute_currency_id', help="The payment's currency.")
    company_id = fields.Many2one('res.company', 'Compañia', default=lambda s: s.env.company, required=True, index=True,
                                 states={'done': [('readonly', True)]})
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'move_pos_id': self.move_pos_id.id,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id
        }
        return payment_vals

    def action_create_payments(self):
        payments = self._create_payments()

    def action_create_view_payments(self):
        payments = self._create_payments()
        action = {
            'name': _('Pagos'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.pos',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action

    def _create_payments(self):
        self.ensure_one()
        payment_vals = self._create_payment_vals_from_wizard()
        payments = self.env['account.payment.pos'].create(payment_vals)
        payments.action_post()
        return payments