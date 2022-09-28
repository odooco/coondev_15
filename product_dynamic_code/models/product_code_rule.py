# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class product_code_rule(models.Model):
    """
    The model which defines rule of constructing an exact code part
    """
    _name = "product.code.rule"
    _description = "Product code rule"

    @api.depends("field_id")
    def _compute_model_from_field_id(self):
        """
        Compute method for model_from_field_id

        Attrs update:
         * model_from_field_id - as model of linked field if exist
        """
        for line in self:
            model_from_field_id = False
            field = line.field_id
            if field and field.ttype in ["many2one", "one2many", "many2many"]:
                model_from_field_id = self.env['ir.model'].search([('model', '=', field.relation)], limit=1,)
            line.model_from_field_id = model_from_field_id

    name = fields.Char(string="Rule", required=True,)
    code_method = fields.Selection(
        [("static", "Static"), ("dynamic", "Dynamic"),],
        string="Code Method",
        default="static",
    )
    code_value = fields.Char(string="Code Value", required=False)
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Field',
        domain=[
            ('ttype', 'in', ['char', 'date', 'datetime', 'float', 'integer', 'monetory', 'selection', 'many2one']),
            ('model', 'in', ['product.product', 'product.template'])
        ],
        ondelete="cascade",
    )
    model_from_field_id = fields.Many2one(
        "ir.model",
        string="Model",
        compute=_compute_model_from_field_id,
        compute_sudo=True,
        store=True,
    )
    related_field_id = fields.Many2one(
        'ir.model.fields',
        string=u"Complementary",
        ondelete="cascade",
    )
    symbol_start = fields.Integer("Symbols", help="Leave 0 to put the whole field value")
    symbol_end = fields.Integer("Symbols end",)
    position_id = fields.Many2one("product.code.position", string="Position",)
    sequence = fields.Integer(
        string="Sequence",
        help="""Only a single rule for each position is applied. Thus, if 2 rules for the same position are found,
        one with a lesser sequence will be chosen""",
    )
    domain = fields.Text(string="Filters", default="[]")

    _order = "sequence, id"

    def _check_product(self, product):
        """
        The method to check whether current product suits domain

        Args:
         * product.product or product.template record

        Returns:
         * bool

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        extra_domain = [("id", "=", product.id), ("manual_code", "=", False), ("manual_template_code", "=", False)]
        domain = extra_domain + safe_eval(self.domain)
        suits = product._search(domain, limit=1) and True or False
        return suits

    def _find_products(self, applied_products):
        """
        The method to find all products by this rule

        Args:
         * applied_products - list of int

        Returns:
         * product.product recordset

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        extra_domain = [
            ("id", "not in", applied_products),
            ("manual_code", "=", False),
            ("manual_template_code", "=", False)
        ]
        domain = extra_domain + safe_eval(self.domain)
        products = self.env["product.product"]._search(domain)
        return products

    def _return_calculated_code(self, product=None):
        """
        Compute method for calculated_code

        Args:
         * product - id of product.product

        Methods:
         * _parse_selection_value

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        res = ""
        if self.code_method == "static":
            res = self.code_value
        else:
            product = self.env["product.product"].browse(product)
            product = self.field_id.model == "product.product" and product or product.product_tmpl_id
            field_name = self.field_id.name
            if self.field_id.ttype == "many2one":
                r_field_name = self.related_field_id.name
                if self.related_field_id.ttype == "selection":
                    cobject = product[field_name]
                    if cobject:
                        res = self._parse_selection_value(cobject, r_field_name)
                else:
                    res = str(product[field_name][r_field_name])
            elif self.field_id.ttype == "selection":
                res = self._parse_selection_value(product, field_name)
            else:
                res = str(product[field_name])
            start = self.symbol_start > 0 and self.symbol_start or 0
            end = self.symbol_end > 0 and self.symbol_end or 10000 #just very big number
            res = res[start:end]
        return res

    @api.model
    def _parse_selection_value(self, cobject, field_name):
        """
        The method to retrieve value of selection field

        Args:
         * cobject - considered instance
         * field_name - char - name of considered field

        Returns:
         * char
        """
        try:
            res = dict((cobject._fields[field_name]._description_selection(self.env)))[cobject[field_name]]
        except:
            res = cobject[field_name]
        return res or ""
