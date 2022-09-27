# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('vendor_bill_id')
    def _onchange_vendor_bill(self):
        if not self.vendor_bill_id:
            return {}
        self.currency_id = self.vendor_bill_id.currency_id
        new_lines = self.env['account.invoice.line']
        for line in self.vendor_bill_id.invoice_line_ids:
            new_lines += new_lines.new(line._prepare_invoice_line())
        self.invoice_line_ids += new_lines
        self.payment_term_id = self.vendor_bill_id.payment_term_id
        self.vendor_bill_id = False
        return {}

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            tax = tax_line.tax_id
            if tax.amount_type == "group":
                for child_tax in tax.children_tax_ids:
                    done_taxes.append(child_tax.id)

            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in tax_line.analytic_tag_ids]
            if tax_line.amount_total:
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': tax_line.amount_total,
                    'quantity': 1,
                    'price': tax_line.amount_total,
                    'account_id': tax_line.account_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'invoice_id': self.id,
                    'tax_ids': [(6, 0, list(done_taxes))] if done_taxes and tax_line.tax_id.include_base_amount else []
                })
            done_taxes.append(tax.id)
        return res