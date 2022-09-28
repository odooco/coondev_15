# -*- coding: utf-8 -*-
import logging
import json
from odoo import fields, models, api, SUPERUSER_ID
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class POSSaleSession(models.Model):
    _name = 'pos.sale.session'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Pos Session Name')
    x_report_sequence = fields.Integer(string='Secuencia de Reporte x', default=0)
    invoice_ids = fields.One2many('account.move', 'pos_session_id', string='Invoices', copy=False)
    point_sale_id = fields.Many2one('point.sale', string='Point of Sale', index=True)
    start_date = fields.Datetime(string='Fecha Inicial')
    start_invoice = fields.Char(string='Factura Inicial')
    end_invoice = fields.Char(string='Factura Final')
    invoice_qyt = fields.Integer(string='Cantidad de Facturas')
    company_id = fields.Many2one('res.company', string="Company", required=True, readonly=True, default=lambda self: self.env.company)
    state = fields.Selection(string='Status', required=True,  copy=False,
    selection=[
        ('open', 'New'),
        ('close', 'Processing')
    ], default='open')

    def close_session(self):
        for item in self:
            item.state = 'close'

    def print_x_report(self):
        self.write({'x_report_sequence': self.x_report_sequence+1})
        return self.env.ref('pos_sale_report.point_sale_session_x_report').report_action(self)


    def _compute_facturas(self):
        for record in self:
            if record.state == 'open':
                record.invoice_qyt = 0
                if not record.start_date:
                    date_start = datetime.now()
                else:
                    date_start = record.start_date
                record.start_date = date_start
                date_end = date_start + timedelta(days=1)
                record.start_invoice = self.env['account.move'].search([('invoice_date','>=',date_start),('invoice_date','<',date_end),('pos_session_id','=',record.id)], order='name asc', limit=1).name
                record.end_invoice = self.env['account.move'].search([('invoice_date','>=',date_start),('invoice_date','<',date_end),('pos_session_id','=',record.id)], order='name desc', limit=1).name
                invoices = self.env['account.move'].search([('invoice_date','>=',date_start),('invoice_date','<',date_end),('pos_session_id','=',record.id)])
                record.invoice_qyt = len(invoices)

    def get_gross_total(self):
        gross_total = 0.0
        if self and self.invoice_ids:
            for invoice in self.invoice_ids.filtered(lambda invoice: invoice.move_type=='out_invoice'):
                gross_total += invoice.amount_total
        return gross_total

    def get_refund_total(self):
        gross_total = 0.0
        if self and self.invoice_ids:
            for invoice in self.invoice_ids.filtered(lambda invoice: invoice.move_type=='out_refund'):
                gross_total += invoice.amount_total
        return gross_total - self.get_total_refund_tax()

    def get_total_tax(self):
        if self and self.invoice_ids:
            total_tax = 0.0
            for invoice in self.invoice_ids.filtered(lambda invoice: invoice.move_type=='out_invoice'):
                total_tax += invoice.amount_tax
        return total_tax - self.get_total_refund_tax()

    def get_total_discount(self):
        total_discount = 0.0
        if self and self.invoice_ids:
            for invoice_id in self.invoice_ids:
                for line in invoice_id.invoice_line_ids:
                    if line.price_subtotal > 0:
                        total_discount += sum([((line.quantity * line.price_unit) * line.discount) / 100])
        return total_discount

    def get_net_gross_total(self):
        net_gross_profit = self.get_gross_total() - self.get_total_tax() + self.get_total_discount() - self.get_refund_total() - self.get_total_refund_tax()
        return net_gross_profit

    def get_total_refund_tax(self):
        if self:
            total_tax = 0.0
            for invoice in self.invoice_ids.filtered(lambda invoice: invoice.move_type=='out_refund'):
                total_tax += invoice.amount_tax
        return total_tax

    def compute_total_payments_amount(self):
        for session in self:
            vals = {}
            for invoice_ids in session.invoice_ids:
                for payment_id in invoice_ids.payment_id:
                    if payment_id.payment_method_id.id not in vals:
                        vals[payment_id.payment_method_id.id] = {
                            'name': payment_id.payment_method_id.name,
                            'amount': payment_id.amount,
                        }
                    else:
                        vals[payment_id.payment_method_id.id]['amount'] += payment_id.amount
            final_list = []
            for a in vals:
                final_list.append(vals.get(a))
            return final_list

    def get_service_category_product(self):
        for session in self:
            vals = {}
            for line_id in session.invoice_ids.invoice_line_ids.filtered(lambda line: line.product_id.type == "service"):
                if line_id.product_id.id not in vals:
                    vals[line_id.product_id.id] = {
                        'name': line_id.product_id.name,
                        'qty': line_id.quantity,
                        'amount': line_id.price_total,
                    }
                else:
                    vals[line_id.product_id.id]['amount'] += line_id.price_total
                    vals[line_id.product_id.id]['qty'] += line_id.quantity
            final_list = []
            for a in vals:
                final_list.append(vals.get(a))
            return final_list

    def get_other_tax_product(self):
        for session in self:
            vals = {}
            final_list = []
            for line_id in session.invoice_ids.invoice_line_ids.filtered(lambda line: line.product_id.type != "service" and line.quantity > 0):
                for tax in line_id.tax_ids:
                    if line_id.move_id.state == 'cancel':
                        continue
                    if tax.name not in vals:
                        vals[tax.name] = {
                            'name': tax.name,
                            'qty': line_id.quantity,
                            'tax': tax.amount,
                            'amount': (line_id.price_subtotal*tax.amount)/100,
                        }
                    else:
                        vals[tax.name]['amount'] += (line_id.price_subtotal*tax.amount)/100
                        vals[tax.name]['qty'] += line_id.quantity
            for a in vals:
                final_list.append(vals.get(a))
            return final_list

    def get_other_category_product(self):
        for session in self:
            vals = {}
            final_list = []
            for line_id in session.invoice_ids.invoice_line_ids.filtered(lambda line: line.product_id.type != "service" and line.quantity > 0):
                if line_id.move_id.state == 'cancel':
                    continue
                if line_id.tax_ids:
                    for tax in line_id.tax_ids:
                        if str(line_id.product_id.categ_id.id)+'-'+ tax.name not in vals:
                            vals[str(line_id.product_id.categ_id.id)+'-'+ tax.name] = {
                                'name': line_id.product_id.categ_id.name +' - '+ tax.name,
                                'qty': line_id.quantity,
                                'tax': line_id.price_total - line_id.price_subtotal,
                                'amount': line_id.price_subtotal,
                            }
                        else:
                            vals[str(line_id.product_id.categ_id.id)+'-'+ tax.name]['tax'] += line_id.price_total - line_id.price_subtotal
                            vals[str(line_id.product_id.categ_id.id)+'-'+ tax.name]['amount'] += line_id.price_subtotal
                            vals[str(line_id.product_id.categ_id.id)+'-'+ tax.name]['qty'] += line_id.quantity
                else:
                    if str(line_id.product_id.categ_id.id) not in vals:
                        vals[str(line_id.product_id.categ_id.id)] = {
                            'name': line_id.product_id.categ_id.name,
                            'qty': line_id.quantity,
                            'tax': line_id.price_total - line_id.price_subtotal,
                            'amount': line_id.price_subtotal,
                        }
                    else:
                        vals[str(line_id.product_id.categ_id.id)]['tax'] += line_id.price_total - line_id.price_subtotal
                        vals[str(line_id.product_id.categ_id.id)]['amount'] += line_id.price_subtotal
                        vals[str(line_id.product_id.categ_id.id)]['qty'] += line_id.quantity
            for a in vals:
                final_list.append(vals.get(a))
            return final_list