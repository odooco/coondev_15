# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class CalendarDayMegatoner(models.Model):
    _name = 'calendar.day.megatoner'

    name = fields.Float(string='Name')
    hour_segment = fields.Selection(string='Hour Segment', selection=[('am', 'AM'), ('pm', 'PM')], Requiered=True, default='am')

    @api.depends('name', 'hour_segment')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            name = str(name) + ' ' + record.hour_segment
            res.append((record.id, name))
        return res