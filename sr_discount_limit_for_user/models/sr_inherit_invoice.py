# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import ValidationError


class srAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.onchange('discount')
    def check_discount_limit(self):
        if self.env.user.discount_limit != 0.00 and self.discount > self.env.user.discount_limit:
            message = "You can only assign maximum " + str(self.env.user.discount_limit) + "% Discount \nContact your administrator for more details"
            raise ValidationError(_(message))
    
    @api.constrains('discount')
    def check_discount_limit_constrains(self):
        for record in self:
            if self.env.user.discount_limit != 0.00 and record.discount > self.env.user.discount_limit:
                message = "You can only assign maximum " + str(self.env.user.discount_limit) + "% Discount \nContact your administrator for more details"
                raise ValidationError(_(message))

