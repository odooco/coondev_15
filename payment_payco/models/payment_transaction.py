# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import sys
from werkzeug import urls
from datetime import datetime

import psycopg2
from dateutil import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo import http
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_payco.controllers.main import PaycoController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payco_payment_ref = fields.Char(string="ePayco Payment Reference")\

    @api.model
    def create(self, vals):
        tx = self.env['payment.transaction'].search([('reference', 'ilike', vals['reference'].split('-')[0] + '%'),
                                                     ('state', 'not in', ('cancel', 'error', 'done'))])
        tx_done = self.env['payment.transaction'].search(
            [('reference', 'ilike', vals['reference'].split('-')[0] + '%'), ('state', '=', 'done')])
        if not tx:
            new_record = super(PaymentTransaction, self).create(vals)
        elif tx_done:
            raise ValidationError('Transaccion de pago en Realizada y Aprobada Anteriormente')
        else:
            raise ValidationError('Transaccion de pago en Proceso')
        return new_record

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return ePayco-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'payco':
            return res

        base_url = self.acquirer_id.get_base_url()
        partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)
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
        lang = 'es' if self.partner_lang == 'es_CO' else 'en'
        external = 'true' if self.acquirer_id.payco_checkout_type == 'standard' else 'false'
        split_reference = self.reference.split('-')
        reference = split_reference[0]
        sql = """select amount_tax from sale_order where name = '%s'
                        """ % (reference)
        http.request.cr.execute(sql)
        result = http.request.cr.fetchall() or []
        amount_tax = 0
        tax = 0
        if not result:
            reference = self.reference
            sql = """select amount_tax from sale_order where name = '%s'
                        """ % (reference)
            http.request.cr.execute(sql)
            result = http.request.cr.fetchall() or []
            if result:
                (amount_tax) = result[0]
        else:
            (amount_tax) = result[0]
        if amount_tax:
            for tax_amount in amount_tax:
                tax = tax_amount
        if tax:
            base_tax = float(float(self.amount) - float(tax))
        else:
            base_tax = float(float(self.amount))
        tx = self.env['payment.transaction'].search([('reference', '=', self.reference)])

        return {
            'public_key': self.acquirer_id.payco_public_key,
            'address1': self.partner_address,
            'amount': self.amount,
            'tax': tax,
            'base_tax': base_tax,
            'city': self.partner_city,
            'country': self.partner_country_id.code,
            'currency_code': self.currency_id.name,
            'email': self.partner_email,
            'first_name': partner_first_name,
            'last_name': partner_last_name,
            "phone_number": '',
            'lang': lang,
            'checkout_external': external,
            "test": testPayment,
            'confirmation_url': urls.url_join(base_url, '/payco/confirmation/backend'),
            'response_url': urls.url_join(base_url, '/payco/redirect/backend'),
            'api_url': urls.url_join(base_url, '/payment/payco/checkout'),
            'extra1': str(tx.id),
            'extra2': self.reference,
            'reference': str(reference)
        }

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Paypal data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'payco':
            return tx
        try:
            tx_id = data.get('x_extra1')
            tx = self.search([('id', '=', int(tx_id)), ('provider', '=', 'payco')])
            if not tx:
                raise ValidationError(
                    "ePayco: " + _("No transaction found")
                )
        except Exception as e:
            raise ValidationError(
                "ePayco: " + _("No transaction found")
            )
        return tx

    def _cron_finalize_post_processing(self):
        txs_to_post_process = self
        if not txs_to_post_process:
            client_handling_limit_date = datetime.now() - relativedelta.relativedelta(minutes=10)
            retry_limit_date = datetime.now() - relativedelta.relativedelta(days=2)
            txs_to_post_process = self.search([
                ('state', '=', 'done'),
                ('is_post_processed', '=', False),
                '|', ('last_state_change', '<=', client_handling_limit_date),
                ('operation', '=', 'refund'),
                ('last_state_change', '>=', retry_limit_date),
            ])
            txs_to_pending_process = self.search([
                ('state', 'in', ('draft', 'pending')),
                ('is_post_processed', '=', False),
                '|', ('last_state_change', '<=', client_handling_limit_date),
                ('operation', '=', 'refund'),
                ('last_state_change', '>=', retry_limit_date),
            ])
        for tx in txs_to_post_process:
            _logger.error(tx._log_received_message())
            try:
                tx._finalize_post_processing()
                self.env.cr.commit()
            except psycopg2.OperationalError:  # A collision of accounting sequences occurred
                self.env.cr.rollback()  # Rollback and try later
            except Exception as e:
                _logger.exception(
                    "encountered an error while post-processing transaction with id %s:\n%s",
                    tx.id, e
                )
                self.env.cr.rollback()
        for tz in txs_to_pending_process:
            tz.state = 'cancel'

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Payco data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_feedback_data(data)
        if self.provider != 'payco':
            return
        tx = ''
        if data:
            sql = """select state from sale_order where name = '%s'
                                        """ % (data.get('x_extra3').split('-')[0])
            http.request.cr.execute(sql)
            result = http.request.cr.fetchall() or []
            if result:
                (state) = result[0]
                model_name = 'sale_order'
            else:
                sql = """select state from account_move where name = '%s'""" % (data.get('x_extra3').split('-')[0])
                http.request.cr.execute(sql)
                result = http.request.cr.fetchall() or []
                (state) = result[0]
                model_name = 'account_move'

            for testMethod in state:
                tx = testMethod
            cod_response = int(data.get('x_cod_response')) if int(data.get('x_cod_response')) else int(
                data.get('x_cod_respuesta'))
            if tx not in ['draft']:
                if cod_response not in [1, 3]:
                    self.manage_status_order(data.get('x_extra3'), model_name)
                else:
                    if cod_response == 1:
                        self.payco_payment_ref = data.get('x_extra2')
                        self.state = 'done'
                        self._set_done()
                        self._finalize_post_processing()
                    elif cod_response == 2:
                        self.payco_payment_ref = data.get('x_extra2')
                        self._set_canceled()
                        self.state = 'cancel'
                    elif cod_response == 3:
                        self._set_pending()
                    else:
                        self.payco_payment_ref = data.get('x_extra2')
                        self.manage_status_order(data.get('x_extra3'), model_name)
                        self.state = 'error'
                        self._set_error(data.get('x_transaction_state'))

            else:
                if cod_response == 1:
                    self.payco_payment_ref = data.get('x_extra2')
                    self._set_done()
                    self._finalize_post_processing()
                    self.state = 'done'
                elif cod_response == 2:
                    self.payco_payment_ref = data.get('x_extra2')
                    self._set_canceled()
                    self.state = 'cancel'
                elif cod_response == 3:
                    self._set_pending()
                else:
                    self.payco_payment_ref = data.get('x_extra2')
                    self.manage_status_order(data.get('x_extra3'), model_name)
                    self.state = 'error'
                    self._set_error(data.get('x_transaction_state'))

    def query_update_status(self, table, values, selectors):
        """ Update the table with the given values (dict), and use the columns in
            ``selectors`` to select the rows to update.
        """
        UPDATE_QUERY = "UPDATE {table} SET {assignment} WHERE {condition} RETURNING id"
        setters = set(values) - set(selectors)
        assignment = ",".join("{0}='{1}'".format(s, values[s]) for s in setters)
        condition = " AND ".join("{0}='{1}'".format(s, selectors[s]) for s in selectors)
        query = UPDATE_QUERY.format(
            table=table,
            assignment=assignment,
            condition=condition,
        )
        self.env.cr.execute(query, values)
        self.env.cr.fetchall()

    def reflect_params(self, name, confirmation=False):
        """ Return the values to write to the database. """
        if not confirmation:
            return {'name': name}
        else:
            return {'origin': name}

    def manage_status_order(self, order_name, model_name, confirmation=False):
        condition = self.reflect_params(order_name, confirmation)
        params = {'state': 'draft'}
        self.query_update_status(model_name, params, condition)

