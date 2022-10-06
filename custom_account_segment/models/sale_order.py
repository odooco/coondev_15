# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types)]

        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal

    def _get_default_journal(self):
        journal_types = ['sale']
        journal = self._search_default_journal(journal_types)
        return journal

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, check_company=True,
                                 domain="[('type', '=', 'sale')]", default=_get_default_journal)

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        count = 0
        for record in invoices:
            if record.journal_id.pos_sale:
                count += 1
        if count == 0:
            return super(SaleOrder, self).action_view_invoice()
        else:
            return super(SaleOrder, self).action_view_invoice()
            # raise ValidationError('Pagina en Construccion')