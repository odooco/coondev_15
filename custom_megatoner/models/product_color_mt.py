# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductColorMt(models.Model):
    _name = 'product.color.megatoner'

    name = fields.Char(string='Name', required=True)
