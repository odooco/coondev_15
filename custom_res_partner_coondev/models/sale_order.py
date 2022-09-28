# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, values):
        for item in self:
            if item.partner_id.state_partner == 'sale_quotation' and 'state' in values and values['state'] == 'sale':
                raise ValidationError(_('El cliente %s es de tipo Prospecto\npor consiguiente no tiene permisos de creacion de Ordenes de Venta\n\nPara mas informaciín contacte con su administrador de sistema') % (item.partner_id.name))
        res = super(SaleOrder, self).write(values)
        return res


