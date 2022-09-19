# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_product(models.Model):
    """
    Overwrite to add a logic of automatic code generation
    """
    _inherit = "product.product"

    manual_code = fields.Boolean(string="Manual Internal Reference")
    manual_template_code = fields.Boolean(related="product_tmpl_id.manual_template_code", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to trigger an additional codes generation

        Methods:
         * action_retrieve_code_parts
        """
        for val in vals_list:
            if val.get("default_code"):
                val.update({"manual_code": True})
        products = super(product_product, self).create(vals_list)
        if not self._context.get("no_regeneration"):
            self.action_retrieve_code_parts()
        return products

    def write(self, values):
        """
        Overwrite to trigger an additional codes generation

        Methods:
         * action_retrieve_code_parts
        """
        res = super(product_product, self).write(values)
        if not self._context.get("no_regeneration"):
            self.action_retrieve_code_parts()
        return res

    def action_retrieve_code_parts(self):
        """
        The method to find all rules related to this product and generate a rule

        Returns:
         * char

        Methods:
         * _find_applicable_rule of product.code.position

        Extra info:
         * we rely open records natural order and hence can break loops safely
        """
        positions = self.env["product.code.position"].search([])
        for product in self:
            if not product.manual_code and not product.manual_template_code:
                codes = []
                for position in positions:
                    code = position._find_applicable_rule(product)
                    codes.append(code)
                product.with_context(no_regeneration=True).default_code = "".join(codes)

    @api.model
    def action_update_dynamic_codes(self):
        """
        The method to update dynamic codes for all products
         1. Construct dict {product ID: code} according to rules (one position rule for each code!)
         2. Update product_product. Apply SQL to avoid an extra browsing
         3. Products which are not found by rules should have an empty code
         4. Trigger template re-calculations

        Methods:
         * _find_products of product.code.rule
         * _compute_default_code of product.template
         * _return_calculated_code of product.code.rule

        Extra info:
         * we do not use action_retrieve_code_parts to avoid search for each product
         * We can't compute and store a code since:
            ** Rules are dynamic
            ** Criteria in rules are dynamic
            ** Search is too long if not to store
         * applied_products is used to make sure the most prioritizes rule is matched
        """
        # 1
        positions = self.env["product.code.position"].search([])
        res_product_rules = {}
        all_products = []
        for position in positions:
            applied_products = []
            for rule in position.rule_ids:
                rule_products = rule._find_products(applied_products)
                for product in rule_products:
                    existing_code = res_product_rules.get(product) or ""
                    res_product_rules[product] = existing_code + rule._return_calculated_code(product)
                applied_products += rule_products
            all_products += applied_products
        # 2
        for product, code in res_product_rules.items():
            query = """UPDATE product_product
                       SET default_code = %s
                       WHERE id = %s"""
            self._cr.execute(query, (code, product))
        # 3
        zero_code_products = self.env["product.product"].search([
            ("id", "not in", all_products),
            ("manual_template_code", "=", False),
            ("manual_code", "=", False),
        ])
        zero_code_products.with_context(no_regeneration=True).write({"default_code": False})
        # 4
        self.env["product.template"].search([])._compute_default_code()
