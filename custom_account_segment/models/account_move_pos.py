# -*- coding: utf-8 -*-

from odoo import models, fields, api, osv, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMovePos(models.Model):
    _name = 'account.move.pos'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = "Facturas Pos"
    _order = 'date desc, name desc, id desc'
    _check_company_auto = True
    _sequence_index = "journal_id"

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_draft(self):
        self.write({'state': 'draft'})

    def action_post(self):
        self.move_id.action_post()
        self.write({'state': 'posted','name': self.move_id.name})

    def preview_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.move_id.get_portal_url(),
        }

    @api.model
    def get_sale_types(self, include_receipts=False):
        return ['out_invoice', 'out_refund'] + (include_receipts and ['out_receipt'] or [])

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])

    def _get_default_journal(self):
        ''' Get the default journal.
                It could either be passed through the context using the 'default_journal_id' key containing its id,
                either be determined by the default type.
                '''
        move_type = self._context.get('default_move_type', 'entry')
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ['sale']
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ['purchase']
        else:
            journal_types = self._context.get('default_move_journal_types', ['general'])

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type not in journal_types:
                raise UserError(_(
                    "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
                    move_type=move_type,
                    journal_type=journal.type,
                ))
        else:
            journal = self._search_default_journal(journal_types)

        return journal

    @api.model
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self._get_default_journal()
        return journal.currency_id or journal.company_id.currency_id

    move_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ], string='Tipo de Movimiento', required=True, store=True, index=True, readonly=True, tracking=True,
        default="entry", change_default=True)

    name = fields.Char(string='Numero', copy=False, compute='_compute_name', readonly=False, store=True, index=True,
                       tracking=True)
    move_id = fields.Many2one('account.move', string='Asiento Contable', index=True, required=True, readonly=True,
                              auto_join=True, ondelete="cascade", check_company=True,
                              help="The move of this entry line.")
    date = fields.Date(string='Fecha', required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]}, copy=False, default=fields.Date.context_today)
    ref = fields.Char(string='Referencia', copy=False, tracking=True)
    narration = fields.Text(string='Terminos y Condiciones')
    state = fields.Selection(selection=[('draft', 'Borrador'), ('posted', 'Publicado'), ('cancel', 'Cancelado')],
                             string='Estado', required=True, readonly=True, copy=False, tracking=True, default='draft')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, check_company=True,
                                 domain="[('type', '=', 'sale')]", default=_get_default_journal)
    company_id = fields.Many2one(comodel_name='res.company', string='Compañia', store=True, readonly=True,
                                 compute='_compute_company_id')
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
                                  states={'draft': [('readonly', False)]}, string='Currency',
                                  default=_get_default_currency)
    line_ids = fields.One2many('account.move.pos.line', 'move_id', string='Lineas de Factura', copy=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    invoice_line_ids = fields.One2many('account.move.pos.line', 'move_id', string='Lineas de Factura', copy=False,
                                       readonly=True, domain=[('exclude_from_invoice_tab', '=', False)],
                                       states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, states={'draft': [('readonly', False)]},
                                 check_company=True, string='Cliente', change_default=True)
    partner_shipping_id = fields.Many2one('res.partner', string='Direccion de Entrega', readonly=True, states={'draft': [('readonly', False)]}, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="Delivery address for current invoice.")
    invoice_user_id = fields.Many2one('res.users', string='Vendedor',
                              help='Technical field used to fit the generic behavior in mail templates.')
    invoice_date = fields.Date(string='Fecha de Factura', readonly=True, index=True, copy=False,
                               states={'draft': [('readonly', False)]})
    invoice_date_due = fields.Date(string='Fecha de Vencimiento', readonly=True, index=True, copy=False,
                                   states={'draft': [('readonly', False)]})
    invoice_origin = fields.Char(string='Documento Origen', copy=False, readonly=False, store=True, index=True,
                                 tracking=True)
    payment_mean_id = fields.Many2one(comodel_name='account.payment.mean', string='Payment Method', copy=False, default=False)

    payment_mean_code_id = fields.Many2one('account.payment.mean.code', string='Mean of Payment',copy=False)

    amount_untaxed = fields.Monetary(string='Total Sin Impuestos', store=True, readonly=True, tracking=True)
    amount_tax = fields.Monetary(string='Impuestos', store=True, readonly=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    amount_residual = fields.Monetary(string='Total pendiente', store=True)
    amount_untaxed_signed = fields.Monetary(string='Valor sin impuesto Signo', store=True, readonly=True)
    amount_tax_signed = fields.Monetary(string='Impuesto Signo', store=True, readonly=True)
    amount_total_signed = fields.Monetary(string='Total Signo', store=True, readonly=True)
    amount_residual_signed = fields.Monetary(string='Amount Due Signed', store=True)
    sale_id = fields.Many2one(string="Sales Order", store=True, readonly=False)


class AccountMovePosLine(models.Model):
    _name = 'account.move.pos.line'
    _description = "Linea Facturas Pos"
    _order = "date desc, move_name desc, id"
    _check_company_auto = True

    move_id = fields.Many2one('account.move.pos', string='Factura Pos', index=True, readonly=True, auto_join=True,
                              ondelete="cascade", help="The move of this entry line.")
    move_name = fields.Char(string='Factura', related='move_id.name', store=True, index=True)
    date = fields.Date(related='move_id.date', store=True, readonly=True, index=True, copy=False, group_operator='min')
    ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=False)
    parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
    journal_id = fields.Many2one(related='move_id.journal_id', store=True, index=True, copy=False)
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True,
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency', readonly=True,
                                          store=True, help='Utility field to express amount currency')
    account_id = fields.Many2one('account.account', string='Account', index=True, ondelete="cascade",
                                 domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
                                 tracking=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nombre', tracking=True)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")
    quantity = fields.Float(string='Cantidad', default=1.0, digits='Product Unit of Measure',
                            help="The optional quantity expressed by this line, eg: number of product sold. The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Float(string='Precio Unitario', digits='Product Price')
    discount = fields.Float(string='Descuento', digits='Discount', default=0.0)
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
    balance = fields.Monetary(string='Balance', store=True, currency_field='company_currency_id',
                              help="Technical field holding the debit - credit in order to open meaningful graph views from reports")
    amount_currency = fields.Monetary(string='Valor en moneda', store=True, copy=True,
                                      help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True, currency_field='currency_id')
    price_total = fields.Monetary(string='Total', store=True, readonly=True, currency_field='currency_id')
    date_maturity = fields.Date(string='Fecha de Vencimiento', index=True, tracking=True,
                                help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', ondelete='restrict')
    product_uom_id = fields.Many2one('uom.uom', string='Unidad de Medida',
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_id = fields.Many2one('product.product', string='Producto', ondelete='restrict')
    product_uom_category_id = fields.Many2one('uom.category', string="Categoria de Producto",
                                              related='product_id.uom_id.category_id')
    tax_ids = fields.Many2many(comodel_name='account.tax', string="Taxes", context={'active_test': False},
                               help="Taxes that apply on the base amount")
    tax_line_id = fields.Many2one('account.tax', string='Impuesto Origen', ondelete='restrict', store=True, help="Indicates that this journal item is a tax line")
    tax_base_amount = fields.Monetary(string="Valor Base", store=True, readonly=True,
                                      currency_field='company_currency_id')
    tax_repartition_line_id = fields.Many2one(comodel_name='account.tax.repartition.line',
                                              string="Originator Tax Distribution Line", ondelete='restrict',
                                              readonly=True,
                                              help="Tax distribution line that caused the creation of this move line, if any")
    tax_tag_ids = fields.Many2many(string="Tags", comodel_name='account.account.tag', ondelete='restrict',
                                   help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.",
                                   tracking=True)
    amount_residual = fields.Monetary(string='Valor Residual', store=True, currency_field='company_currency_id',
                                      help="The residual amount on a journal item expressed in the company currency.")
    amount_residual_currency = fields.Monetary(string='Residual Amount in Currency', store=True,
                                               help="The residual amount on a journal item expressed in its currency (possibly not the company currency).")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True, store=True,
                                          readonly=False, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
                                        compute="_compute_analytic_account", store=True, readonly=False, copy=True)
    exclude_from_invoice_tab = fields.Boolean(
        help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")
