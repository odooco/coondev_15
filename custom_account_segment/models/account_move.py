# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for record in self:
            if record.journal_id.st_dt:
                rc_lines = record.line_ids.filtered(lambda line: line.st_dt)
                if not rc_lines:
                    lines = []
                    pos_lines = []
                    new_lines = []
                    old_lines = record.line_ids
                    for line in record.line_ids:
                        if line.name:
                            name = 'rec -' + line.name
                        else:
                            name = 'Reclacificacion'
                        if line.name and 'IVA' in line.name:
                            account = self.env.user.company_id.tax_account_id.id
                        elif line.credit:
                            account = self.env.user.company_id.end_account_id.id
                        else:
                            account = self.env.user.company_id.general_account_id.id
                        pos_lines.append({
                            'name': line.name,
                            'account_id': line.account_id.id,
                            'product_id': line.product_id.id,
                            'currency_id': record.currency_id.id,
                            'company_id': record.company_id.id,
                            'debit': line.debit,
                            'credit': line.credit,
                            'exclude_from_invoice_tab': line.exclude_from_invoice_tab,
                            'tax_ids': line.tax_ids.ids,
                            'discount': line.discount,
                            'display_type': line.display_type,
                            'price_unit': line.price_unit,
                            'tax_repartition_line_id': line.tax_repartition_line_id.id,
                            'tax_tag_ids': line.tax_tag_ids.ids,
                            'tax_base_amount': line.tax_base_amount,
                            'amount_residual': line.amount_residual,
                            'price_subtotal': line.price_subtotal,
                            'quantity': line.quantity,
                        })
                        lines.append({
                            'name': name,
                            'account_id': account,
                            'move_id': line.move_id.id,
                            'debit': line.debit * self.env.user.company_id.percent_rec / 100,
                            'credit': line.credit * self.env.user.company_id.percent_rec / 100,
                            'exclude_from_invoice_tab': True,
                            'st_dt': True,
                            'quantity': line.quantity,
                        })
                        new_lines.append({
                            'name': line.name,
                            'account_id': line.account_id.id,
                            'product_id': line.product_id.id,
                            'move_id': line.move_id.id,
                            'debit': line.debit * (100 - self.env.user.company_id.percent_rec) / 100,
                            'credit': line.credit * (100 - self.env.user.company_id.percent_rec) / 100,
                            'exclude_from_invoice_tab': line.exclude_from_invoice_tab,
                            'tax_ids': line.tax_ids.ids,
                            'discount': line.discount,
                            'price_unit': line.price_unit,
                            'tax_repartition_line_id': line.tax_repartition_line_id.id,
                            'tax_tag_ids': line.tax_tag_ids.ids,
                            'tax_base_amount': line.tax_base_amount,
                            'amount_residual': line.amount_residual,
                            'price_subtotal': line.price_subtotal,
                            'quantity': line.quantity,
                        })
                    old_lines.sudo().unlink()
                    self.env['account.move.line'].sudo().create(new_lines)
                    lines_new_move = self.env['account.move.line'].sudo().create(lines)
                    record.move_type = 'entry'
                    res = super(AccountMove, self).action_post()
                    invoice = self.sudo().create({
                        'move_type': 'entry',
                        'partner_id': self.env.user.company_id.partner_rec.id,
                        'currency_id': self.currency_id.id,
                        'invoice_date': self.invoice_date,
                        'journal_id': self.env.user.company_id.journal_id.id,
                        'date': self.date,
                        'line_ids': lines_new_move.ids
                    })
                    invoice.sudo().action_post()
                    pos_lines_new = self.env['account.move.pos.line'].sudo().create(pos_lines)
                    self.env['account.move.pos'].sudo().create({
                        'name': record.name,
                        'move_id': record.id,
                        'move_type': 'out_invoice',
                        'ref': record.ref,
                        'narration': record.ref,
                        'partner_id': record.partner_id.id,
                        'payment_mean_id': record.payment_mean_id.id,
                        'payment_mean_code_id': record.payment_mean_code_id.id,
                        'partner_shipping_id': record.partner_shipping_id.id,
                        'invoice_user_id': record.invoice_user_id.id,
                        'state': 'posted',
                        'company_id': record.company_id.id,
                        'invoice_origin': record.invoice_origin,
                        'currency_id': record.currency_id.id,
                        'invoice_date': record.invoice_date,
                        'amount_untaxed': record.amount_untaxed,
                        'amount_tax': record.amount_tax,
                        'amount_total': record.amount_total,
                        'amount_residual': record.amount_residual,
                        'amount_untaxed_signed': record.amount_untaxed_signed,
                        'amount_tax_signed': record.amount_tax_signed,
                        'amount_total_signed': record.amount_total_signed,
                        'amount_residual_signed': record.amount_residual_signed,
                        'journal_id': record.journal_id.id,
                        'date': record.date,
                        'line_ids': pos_lines_new.ids
                    })
                else:
                    res = super(AccountMove, self).action_post()
            elif record.journal_id.pos_sale:
                record.move_type = 'entry'
            else:
                res = super(AccountMove, self).action_post()
        return res