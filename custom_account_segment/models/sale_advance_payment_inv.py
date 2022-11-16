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
            self._context['open_invoices'] = False
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for record in sale_orders:
            invoices = record.mapped('invoice_ids')
            for invoice in invoices:
                if invoice.journal_id.pos_sale:
                    invoice.create_pos(record.id)
                    invoice.journal_id = record.journal_id
            record.invoice_status = 'invoiced'
        return res

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        res["journal_id"] = sale_orders.journal_id.id
        return res

    def action_view_invoice(self):
        if not self.invoice_pos_ids:
            res = super(SaleAdvancePaymentInv, self).create_invoices()
        else:
            invoices = self.mapped('invoice_pos_ids')
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                form_view = [(self.env.ref('account_move_pos_views.xml.view_move_pos_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = invoices.id
            else:
                action = {'type': 'ir.actions.act_window_close'}

            context = {
                'default_move_type': 'out_invoice',
            }
            if len(self) == 1:
                context.update({
                    'default_partner_id': self.partner_id.id,
                    'default_partner_shipping_id': self.partner_shipping_id.id,
                    'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                    'default_invoice_origin': self.name,
                    'default_user_id': self.user_id.id,
                })
            action['context'] = context
            res = action
        return res