from odoo import api, fields, models
from odoo.addons.payment_payco.const import SUPPORTED_CURRENCIES
import uuid

class SaleOrder(models.Model):
    _inherit = "sale.order"

    check_payco_button = fields.Boolean(string="Payment Buttom", copy=False)

    def email_payment(self):
        self.access_token = self.access_token if self.access_token else str(uuid.uuid4())
        template = self.env.ref('payment_payco.email_template_for_epayco')
        if template:
            template.email_from = str(self.env.user.partner_id.email)
            template.attachment_ids = [(5, 0, [])]
            template.send_mail(self.id, force_send=True)
            self.check_payco_button = True