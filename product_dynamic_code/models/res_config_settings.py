# -*- coding: utf-8 -*-

from odoo import models


class res_config_settings(models.TransientModel):
    """
    Re-wrtie to have a quick link from settings to quick codes
    """
    _inherit = 'res.config.settings'

    def action_update_product_codes(self):
        """
        The method to launch all product codes re-generation

        Methods:
         * action_update_dynamic_codes of product.product
        """
        cron_id = self.env.ref("product_dynamic_code.construct_dynamic_codes")
        cron_id.method_direct_trigger()
