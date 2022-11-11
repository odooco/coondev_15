# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict

class AccountPaymentPosRegister(models.TransientModel):
    _name = 'account.payment.pos.register'
    _description = 'Register Payment Pos'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'line_ids' in fields_list and 'line_ids' not in res:
            if self._context.get('active_model') == 'account.move.pos':
                lines = self.env['account.move.pos'].browse(self._context.get('active_ids', [])).line_ids
            elif self._context.get('active_model') == 'account.move.pos.line':
                lines = self.env['account.move.pos.line'].browse(self._context.get('active_ids', []))
            else:
                raise UserError(_(
                    "The register payment wizard should only be called on account.move.pos or account.move.pos.line records."
                ))

            if 'journal_id' in res and not self.env['account.journal'].browse(res['journal_id'])\
                    .filtered_domain([('company_id', '=', lines.company_id.id), ('type', 'in', ('bank', 'cash'))]):
                del res['journal_id']

            available_lines = self.env['account.move.pos.line']
            for line in lines:
                if line.move_id.state != 'posted' and line.move_id.state != 'post':
                    raise UserError(_("You can only register payment for posted journal entries."))
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                available_lines |= line
            res['line_ids'] = [(6, 0, available_lines.ids)]
        return res

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for wizard in self:
            wizard.available_payment_method_line_ids = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
            if wizard.payment_method_line_id.id in wizard.available_payment_method_line_ids.ids:
                wizard.available_payment_method_line_ids.code == 'manual'

    def _get_batches(self):
        self.ensure_one()
        lines = self.line_ids

        batches = defaultdict(lambda: {'lines': self.env['account.move.pos.line']})
        for line in lines:
            batch_key = self._get_line_batch_key(line)
            serialized_key = '-'.join(str(v) for v in batch_key.values())
            vals = batches[serialized_key]
            vals['payment_values'] = batch_key
            vals['lines'] += line

        # Compute 'payment_type'.
        for vals in batches.values():
            lines = vals['lines']
            balance = sum(lines.mapped('balance'))
            vals['payment_values']['payment_type'] = 'inbound' if balance > 0.0 else 'outbound'

        return list(batches.values())

    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ], limit=1)

    @api.model
    def _get_batch_available_partner_banks(self, batch_result, journal):
        payment_values = batch_result['payment_values']
        company = batch_result['lines'].company_id

        if payment_values['payment_type'] == 'inbound':
            return journal.bank_account_id
        else:
            return batch_result['lines'].partner_id.bank_ids.filtered(lambda x: x.company_id.id in (False, company.id))._origin

    @api.depends('journal_id', 'available_partner_bank_ids')
    def _compute_partner_bank_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                partner_bank_id = batch['payment_values']['partner_bank_id']
                available_partner_banks = wizard.available_partner_bank_ids._origin
                if partner_bank_id and partner_bank_id in available_partner_banks.ids:
                    wizard.partner_bank_id = self.env['res.partner.bank'].browse(partner_bank_id)
                else:
                    wizard.partner_bank_id = available_partner_banks[:1]
            else:
                wizard.partner_bank_id = None

    @api.depends('journal_id')
    def _compute_available_partner_bank_ids(self):
        for wizard in self:
            batch = wizard._get_batches()[0]
            wizard.available_partner_bank_ids = wizard._get_batch_available_partner_banks(batch, wizard.journal_id)

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_id(self):
        for wizard in self:
            available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
            if available_payment_method_lines:
                wizard.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                wizard.payment_method_line_id = False

    # == Business fields ==
    payment_date = fields.Date(string="Payment Date", required=True,
                               default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
                             compute='_compute_amount')
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 compute='_compute_journal_id',
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    communication = fields.Char(string="Memo", store=True, readonly=False,
                                compute='_compute_communication')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
    )
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Recipient Bank Account",
        readonly=False,
        store=True,
        compute='_compute_partner_bank_id',
        domain="[('id', 'in', available_partner_bank_ids)]",
    )

    # == Fields given through the context ==
    line_ids = fields.Many2many('account.move.pos.line', 'account_payment_register_move_pos_line_rel', 'wizard_id', 'line_id',
                                string="Journal items", readonly=True, copy=False)
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money')], string='Payment Type', store=True, copy=False,
        compute='_compute_from_lines')
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], store=True, copy=False,
        compute='_compute_from_lines')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 compute='_compute_from_lines')
    partner_id = fields.Many2one('res.partner',
                                 string="Customer/Vendor", store=True, copy=False, ondelete='restrict',
                                 compute='_compute_from_lines')
    # == Payment methods fields ==
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
                                             readonly=False, store=True,
                                             compute='_compute_payment_method_line_id',
                                             domain="[('id', 'in', available_payment_method_line_ids)]",
                                             help="Manual: Pay or Get paid by any method outside of Odoo.\n"
                                                  "Payment Acquirers: Each payment acquirer has its own Payment Method. Request a transaction on/to a card thanks to a payment token saved by the partner when buying or subscribing online.\n"
                                                  "Check: Pay bills by check and print it from Odoo.\n"
                                                  "Batch Deposit: Collect several customer checks at once generating and submitting a batch deposit to your bank. Module account_batch_payment is necessary.\n"
                                                  "SEPA Credit Transfer: Pay in the SEPA zone by submitting a SEPA Credit Transfer file to your bank. Module account_sepa is necessary.\n"
                                                  "SEPA Direct Debit: Get paid in the SEPA zone thanks to a mandate your partner will have granted to you. Module account_sepa is necessary.\n")
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')
    country_code = fields.Char(related='company_id.account_fiscal_country_id.code', readonly=True)

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
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
        if self._context.get('dont_redirect_to_payments'):
            return True
        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
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
        batches = self._get_batches()
        edit_mode = len(batches[0]['lines']) == 1 or self.group_payment
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': batches[0]['lines'],
                'batch': batches[0],
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        self._post_payments(to_process, edit_mode=edit_mode)
        self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments