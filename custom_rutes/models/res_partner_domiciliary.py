# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResPartnerDomiciliary(models.Model):
    _name = 'res.partner.domiciliary'
    _order='sequence'

    sequence=fields.Integer("sequence", default=1)
    name = fields.Char(string='Nombre')
    mobile = fields.Char(string='Celular')
    date_processing = fields.Datetime(string='Fecha de Procesamiento', default=lambda self: fields.Datetime.now())
    company_id = fields.Many2one('res.company', string='Compañia')
    latitude = fields.Float(string='Latitud', digits=(10, 7))
    longitude = fields.Float(string='Longitud', digits=(10, 7))
    active = fields.Boolean(string='Activo', default=True)