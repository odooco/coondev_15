# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    partner_rec = fields.Many2one('res.partner', string='Contacto de Reclasificacion')
    percent_rec = fields.Float(string='Porcentaje de reclacificacion', digits=(16, 1))
    general_account_id = fields.Many2one('account.account', string='Cuenta de Segmentacion Entrada', ondelete='restrict')
    tax_account_id = fields.Many2one('account.account', string='Cuenta de Segmentacion Impuestos', ondelete='restrict')
    end_account_id = fields.Many2one('account.account', string='Cuenta de Segmentacion Salida', ondelete='restrict')
