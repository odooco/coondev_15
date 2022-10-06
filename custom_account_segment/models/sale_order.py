# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        count = 0
        for record in invoices:
            if record.journal_id.pos_sale:
                count += 1
        if count > 0:
            raise ValidationError('Pagina en Construccion')
        else:
            action = super(SaleOrder, self).action_view_invoice()
        return action