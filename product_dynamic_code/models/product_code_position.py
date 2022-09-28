# -*- coding: utf-8 -*-

from odoo import fields, models


class product_code_position(models.Model):
    """
    The model which defines each position of product code
    """
    _name = "product.code.position"
    _description = "Product code position"

    name = fields.Char(string="Reference", required=True,)
    sequence = fields.Integer(
        string="Position",
        help="Where this part of code should be placed in relation to other parts",
        default=1,
    )
    rule_ids = fields.One2many("product.code.rule", "position_id", string="Rules")
    active = fields.Boolean(string="Active",default=True)

    _order = "sequence, id"


    def _find_applicable_rule(self, product):
        """
        The method to loop over rules to find applicable

        Args:
         * product - product.product

        Returns:
         * char (empty if no rule found for position)

        Methods:
         * _check_product of product.code.rule
         * _return_calculated_code of product.code.rule

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        code = ""
        for rule in self.rule_ids:
            suits = rule._check_product(product)
            if suits:
                code = rule._return_calculated_code(product.id)
                break
        return code
