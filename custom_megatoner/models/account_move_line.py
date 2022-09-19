# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def account_partner_compute(self):
        for item in self:
            if item.move_id.move_type == 'out_invoice' and not item.partner_id:
                item.partner_id = item.move_id.partner_id