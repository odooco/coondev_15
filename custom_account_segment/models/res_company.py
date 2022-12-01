# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    partner_rec = fields.Many2one('res.partner', string='Contacto de Reclasificacion')
    percent_rec = fields.Float(string='Porcentaje de reclacificacion', digits=(16, 1))
    general_account_id = fields.Many2one('account.account', string='Cuenta de Efectivo', ondelete='restrict')
    tax_account_id = fields.Many2one('account.account', string='Cuenta de Segmentacion Impuestos', ondelete='restrict')
    end_account_id = fields.Many2one('account.account', string='Cuenta de Ingreso', ondelete='restrict')
    payment_account_id = fields.Many2one('account.account', string='Cuenta de Caja General', ondelete='restrict')
    journal_id = fields.Many2one(comodel_name="account.journal", string="Diario Reclacificaciones",
                                 domain="[('type', '=', 'sale')]")

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_pos_invoiced(self):
        for partner in self:
            invoices = self.env['account.move.pos'].search([('partner_id', '=', partner.id)])
            partner.invoice_pos_ids = invoices
            partner.invoice_pos_count = len(invoices)

    invoice_pos_count = fields.Integer(string='Invoice Count', compute='_get_pos_invoiced', readonly=True)
    invoice_pos_ids = fields.Many2many("account.move.pos", 'sale_move_pos_rel', 'sale_id', 'move_pos_id',
                                       string='Invoices', compute="_get_pos_invoiced",
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
                'default_partner_id': self.id,
                'default_invoice_payment_term_id': self.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
            })
        action['context'] = context
        return action