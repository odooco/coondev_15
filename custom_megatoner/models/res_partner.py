# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    weekly_schedule_am = fields.Many2many('calendar.day.megatoner', 'c_day_weekly_am_rel', 'partner_id', 'calendar_day_id', string='Weekly Schedule Am')
    weekly_schedule_pm = fields.Many2many('calendar.day.megatoner', 'c_day_weekly_pm_rel', 'partner_id', 'calendar_day_id', string='Weekly Schedule Am')
    saturday_schedule_am = fields.Many2many('calendar.day.megatoner', 'c_day_saturday_am_rel', 'partner_id', 'calendar_day_id', string='Saturday Schedule AM')
    saturday_schedule_pm = fields.Many2many('calendar.day.megatoner',  'c_day_saturday_pm_rel', 'partner_id', 'calendar_day_id',string='Saturday Schedule AM')

    @api.onchange('weekly_schedule_am','weekly_schedule_pm','saturday_schedule_am','saturday_schedule_pm')
    def _onchange_weekly_schedule(self):
        for item in self:
            if len(item.weekly_schedule_am)>2:
                raise ValidationError('Defina solamente 2 horas para el horario semanal en la mañana')
            if len(item.weekly_schedule_pm)>2:
                raise ValidationError('Defina solamente 2 horas para el horario semanal en la tarde')
            if len(item.saturday_schedule_am)>2:
                raise ValidationError('Defina solamente 2 horas para el horario sabatino en la mañana')
            if len(item.saturday_schedule_pm)>2:
                raise ValidationError('Defina solamente 2 horas para el horario sabatino en la tarde')