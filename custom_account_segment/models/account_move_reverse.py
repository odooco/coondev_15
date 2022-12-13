# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict

class AccountMoveReverse(models.TransientModel):
    _name = 'account.move.reverse'
    _description = 'Creacion de Notas Pos'

    move_pos_id = fields.Many2one(comodel_name='account.move.pos', string='Factura', readonly=True, ondelete='cascade')
    journal_id = fields.Many2one('account.journal', string='Diario', required=True, domain="[('type', '=', 'sale')]")

    def action_create_refund(self):
        self.move_pos_id.action_reverse(self.journal_id.id)

    def action_create_view_refund(self):
        self.ensure_one()
        refunds = self.move_pos_id.action_reverse(self.journal_id.id)
        action = {
            'name': _('Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.pos',
            'context': {'create': False},
        }
        if len(refunds) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': refunds.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', refunds.ids)],
            })
        return action