# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class RouteActivity(models.Model):
    _name = 'route.activity'

    name = fields.Char(string='Descripción')
    active_model_ids = fields.Many2many('ir.model', 'ir_models_activity_rel', 'route_activity_id', 'res_models_id', string='Modulo Disponible')