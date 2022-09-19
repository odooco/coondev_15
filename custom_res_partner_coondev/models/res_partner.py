# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    state_partner = fields.Selection([
        ('sale_quotation', 'prospect'),
        ('point_of_sale', 'sale_client'),
        ('accountant_third', 'Third accountant')], string="State", default="sale_quotation")

    tax_identification = fields.Binary(string='RUT' ,tracking=True)
    create_template_client = fields.Binary(string='Formato de Creacion de Clientes' ,tracking=True)
    tax_identification_store = fields.Binary(string='Camara y Comercio' ,tracking=True)
    bank_certification = fields.Binary(string='Certificacion Bancaria' ,tracking=True)
    journal_id = fields.Many2one('account.journal', string='Diario Venta', domain="[('type', '=', 'sale')]")