# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import sys
from pprint import pprint

from odoo.fields import Command

from requests.exceptions import ConnectionError, HTTPError
from werkzeug import urls
import requests
from odoo import _, http
from odoo.exceptions import ValidationError, MissingError, AccessError
from odoo.http import request, Response
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

import json

_logger = logging.getLogger(__name__)


class PaymentPortal(payment_portal.PaymentPortal):

    @http.route('/payment_epayco/<string:invoice_id>/<string:token_id>', type='http', auth='none')
    def payment_epayco(self, token_id, **kwargs):
        invoice_id = request.env['account.move'].sudo().search([('access_token', '=', token_id), ], limit=1)
        if not invoice_id:
            return request.not_found()
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payco')], limit=1)
        partner_first_name, partner_last_name = payment_utils.split_partner_name(invoice_id.partner_id.name)
        base_url = request.env['ir.config_parameter'].sudo().sudo().get_param('web.base.url')
        external = 'true' if acquirer_id.payco_checkout_type == 'standard' else 'false'
        testPayment = 'true'

        tx = request.env['payment.transaction'].sudo().search(
            [('token_id', '=', invoice_id.access_token), ('state', '!=', 'done'), ('state', '!=', 'cancel')])
        tx_paid = request.env['payment.transaction'].sudo().search(
            [('token_id', '=', invoice_id.access_token), ('state', '=', 'done')])
        if not tx:
            tx = request.env['payment.transaction'].sudo().create({
                'amount': invoice_id.amount_total,
                'acquirer_id': acquirer_id.id,
                # 'token_id': token_id.id,
                'currency_id': invoice_id.currency_id.id,
                'reference': invoice_id.invoice_origin,
                'partner_id': invoice_id.partner_id.id,
                'partner_name': invoice_id.partner_id.name,
                'partner_lang': invoice_id.partner_id.lang,
                'partner_email': invoice_id.partner_id.email,
                'partner_address': invoice_id.partner_id.street,
                'partner_zip': invoice_id.partner_id.zip,
                'partner_city': invoice_id.partner_id.city,
                'partner_state_id': invoice_id.partner_id.state_id.id,
                'partner_country_id': invoice_id.partner_id.country_id.id,
                'partner_phone': invoice_id.partner_id.phone,
            })
            return {
                'public_key': acquirer_id.payco_public_key,
                'address1': invoice_id.partner_id.street,
                'amount': invoice_id.amount_total,
                'tax': invoice_id.amount_tax,
                'base_tax': invoice_id.amount_untaxed,
                'city': invoice_id.partner_id.city,
                'country': invoice_id.partner_id.country_id.code,
                'currency_code': invoice_id.currency_id.name,
                'email': invoice_id.partner_id.email,
                'first_name': partner_first_name,
                'last_name': partner_last_name,
                "phone_number": invoice_id.partner_id.phone,
                'lang': invoice_id.partner_id.lang,
                'checkout_external': external,
                "test": testPayment,
                'confirmation_url': urls.url_join(base_url, '/payco/confirmation/backend'),
                'response_url': urls.url_join(base_url, '/payco/redirect/backend'),
                'api_url': urls.url_join(base_url, '/payment/payco/checkout'),
                'extra1': str(tx.id),
                'extra2': invoice_id.partner_id.vat,
                'reference': str(invoice_id.name)
            }
        elif tx_paid:
            raise ValidationError('Ya hay Una Transaccion de Pago aprobada para esta factura')
        else:
            raise ValidationError('Hay Una Transaccion de Pago por Epayco en Proceso')

    @http.route(
        '/payco/payment/transaction/<int:invoice_id>/<string:access_token>', type='json', auth='public', website=True
    )
    def payco_payment_transaction(self, invoice_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            self._document_check_access('account.move', invoice_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError("The access token is invalid.")

        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        tx_sudo = self._create_transaction(
            custom_create_values={'invoice_ids': [Command.set([invoice_id])]}, **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        last_tx_id = request.session.get('__backend_payment_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentPostProcessing.remove_transactions(last_tx)
        request.session['__backend_payment_last_tx_id'] = tx_sudo.id

        return tx_sudo._get_processing_values()

    @http.route(
        '/payco/redirect/backend', type='http', auth='public', website=True, csrf=False, save_session=False
    )
    def payco_backend_redirec(self, **post):
        return self._payco_process_response(post)

    def _payco_process_response(self, data):
        ref_payco = data.get('ref_payco')
        if ref_payco is None:
            return request.redirect('/shop/payment')
        url = 'https://secure.epayco.co/validation/v1/reference/%s' % (
            ref_payco)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data')
            request.env['payment.transaction'].sudo()._handle_feedback_data('payco', data)
            return request.redirect('/payment/status')
        else:
            return request.redirect('/shop/payment')

    @http.route(
        '/payco/confirmation/backend', type='http', auth='public', website=True, csrf=False, save_session=False
    )
    def payco_confirmation_redirec(self, **post):
        request.env['payment.transaction'].sudo()._handle_feedback_data('payco', post)
        return request.redirect('/payment/status')


class PaycoController(http.Controller):
    _return_url = '/payment/payco/response/'
    _confirm_url = '/payment/payco/confirm/'
    _proccess_url = '/payment/payco/checkout'

    @http.route(['/payment/payco/checkout'], type='http', auth='public', website=True, csrf=False, save_session=False)
    def epayco_checkout(self, **post):
        """ Epayco."""
        return request.render('payment_payco.proccess', post)

    @http.route('/payment/payco/transction/process', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def payco_transction_process(self, **data):
        try:
            if not data.get('reference'):
                raise ValidationError("Payco: " + _("Transaction not Created"))

            tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', data.get('reference'))])
            acquirer_sudo = request.env['payment.acquirer'].sudo().search([('id', '=', int(data.get('acquirer_id')))])

            res = self.payco_create_indention(tx_sudo, acquirer_sudo, **data)
            if not res:
                raise ValidationError("Payco: " + _("Transaction not Created"))
            datas = json.dumps(res)
            return json.dumps(datas)

        except Exception as e:
            return Response(str(e), status=500)

    def payco_create_indention(self, tx_id=None, acquirer_sudo=None, **data):
        sqlCurrency = """select name from res_currency where active = '%s'
                                """ % (True)
        http.request.cr.execute(sqlCurrency)
        resultCurrency = http.request.cr.fetchall() or []
        if resultCurrency:
            (name) = resultCurrency[0]
        for currencyName in name:
            currency = currencyName

        sqlTestMethod = """select state from payment_acquirer where provider = '%s'
                        """ % ('payco')
        http.request.cr.execute(sqlTestMethod)
        resultTestMethod = http.request.cr.fetchall() or []
        if resultTestMethod:
            (state) = resultTestMethod[0]
        for testMethod in state:
            test = testMethod
        testPayment = 'true' if test == 'test' \
            else 'false'

        plit_reference = data.get('reference').split('-')
        sql = """select amount_tax from sale_order where name = '%s'
                """ % (plit_reference[0])
        http.request.cr.execute(sql)
        result = http.request.cr.fetchall() or []
        if result:
            (amount_tax) = result[0]
        for tax_amount in amount_tax:
            tax = tax_amount
        base_tax = float(float(data.get('amount')) - float(tax))
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        response_url = urls.url_join(base_url, '/payco/redirect/backend')
        confirmation_url = urls.url_join(base_url, '/payco/confirmation/backend')
        external = 'true' if acquirer_sudo.payco_checkout_type == 'standard' else 'false'

        payload = {
            "public_key": acquirer_sudo.payco_public_key,
            "txnid": str(plit_reference[0]),
            "amount": str(data.get('amount')),
            "tax": str(tax),
            'base_tax': str(base_tax),
            'productinfo': data.get('reference'),
            "first_name": tx_id.partner_id.name,
            "email": tx_id.partner_id.email,
            "currency": currency,
            "lang": 'es',
            "test": testPayment,
            "country": tx_id.partner_id.country_id.code if tx_id.partner_id.country_id else "",
            "city": tx_id.partner_id.city,
            "phone_number": tx_id.partner_id.phone.replace(' ', ''),
            "reference": str(plit_reference[0]),
            "extra1": str(tx_id.id),
            'extra2': data.get('reference'),
            "response_url": response_url,
            "confirmation_url": confirmation_url,
            "checkoutType": external
        }
        return payload

