# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'sale')]")

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        count = 0
        for record in invoices:
            if record.journal_id.pos_sale:
                count += 1
        if count == 0:
            return super(SaleOrder, self).action_view_invoice()
        else:
            return super(SaleOrder, self).action_view_invoice()
            # raise ValidationError('Pagina en Construccion')