# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    st_dt = fields.Boolean(default=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    st_dt = fields.Boolean(default=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        for record in self:
            res = super(AccountMove, self).write(vals)
            if record.journal_id.st_dt:
                rc_lines = record.line_ids.filtered(lambda line: line.st_dt)
                if not rc_lines:
                    lines = []
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
                        lines.append({
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
                    old_lines.unlink()
                    """
                        if line.debit:
                            line.write({'debit': line.credit * (100 - self.env.user.company_id.percent_rec) / 100})
                        else:
                            line.write({'credit': line.debit * (100 - self.env.user.company_id.percent_rec) / 100})"""
                    self.env['account.move.line'].create(lines)
        return res