# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, values):
        res = super(AccountMove, self).create(values)
        for item in res:
            item.calculate_journal_id()
            if item.partner_id.state_partner == 'sale_quotation':
                raise ValidationError(_('El cliente %s es de tipo Prospecto\npor consiguiente no tiene permisos de creacion de facturas\n\nPara mas informaciín contacte con su administrador de sistema') % (item.partner_id.name))
        return res

    @api.onchange('partner_id')
    def calculate_journal_id(self):
        for item in self:
            if item.partner_id.journal_id and item.move_type=='out_invoice':
                item.journal_id = item.partner_id.journal_id