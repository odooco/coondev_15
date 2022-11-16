# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        vista = False
        if self._context.get('open_invoices', False):
            self.env.context['open_invoices'] = False
            vista = True
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for record in sale_orders:
            invoices = record.mapped('invoice_ids')
            for invoice in invoices:
                if invoice.journal_id.pos_sale:
                    invoice.create_pos(record.id)
                    invoice.journal_id = record.journal_id
            record.invoice_status = 'invoiced'
        if vista:
            return sale_orders.action_view_invoice()
        return res

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        res["journal_id"] = sale_orders.journal_id.id
        return res
