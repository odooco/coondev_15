# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pos_sale = fields.Boolean('Is Point Sale?', index=True)
    pos_sale_id = fields.Many2one('point.sale', string='Session Pos', index=True)