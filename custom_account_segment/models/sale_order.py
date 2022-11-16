# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.invoice_lines')
    def _get_pos_invoiced(self):
        for order in self:
            invoices = self.env['account.move.pos'].search([('sale_id', '=', order.id)])
            order.invoice_pos_ids = invoices
            order.invoice_pos_count = len(invoices)

    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'sale')]")
    invoice_pos_count = fields.Integer(string='Invoice Count', compute='_get_pos_invoiced', readonly=True)
    invoice_pos_ids = fields.Many2many("account.move.pos", string='Invoices', compute="_get_pos_invoiced",
                                       readonly=True, copy=False)

    def action_pos_view_invoice(self):
        invoices = self.invoice_pos_ids
        action = self.env["ir.actions.actions"]._for_xml_id("custom_account_segment.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('custom_account_segment.view_move_pos_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
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
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def action_view_invoice(self):
        self.ensure_one()
        invoices = self.mapped('invoice_pos_ids')
        if not invoices and self.journal_id.pos_sale:
            return True
        count = 0
        for record in invoices:
            count += 1
        if count == 0:
            return super(SaleOrder, self).action_view_invoice()
        else:
            return self.action_pos_view_invoice()