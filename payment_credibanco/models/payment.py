# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import uuid
import requests
from requests.exceptions import HTTPError
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.addons.payment_credibanco.controllers.main import CredibancoController
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class PaymentTransactionCredibanco(models.Model):
    _inherit = 'payment.transaction'

    reference2=fields.Char(Index=True)


class PaymentAcquirerCredibanco(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(string="Payment",selection_add=[('credibanco', 'Credibanco')], ondelete={'credibanco': 'set default'})
    userName = fields.Char(string="Usuario", required_if_provider='credibanco', groups='base.group_user')
    password = fields.Char(string="Password", required_if_provider='credibanco', groups='base.group_user')
    

    

    @api.model
    def _get_credibanco_urls(self, acquirer):
        if acquirer == 'prod':
            return 'https://eco.credibanco.com/payment/rest/register.do'
        return 'https://ecouat.credibanco.com/payment/rest/register.do'
    
    def _credibanco_request(self, data=False, method='POST'):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        url = self._get_credibanco_urls(environment)
        headers = {}
        resp = requests.request(method, url, data=data, headers=headers)
        if not resp.ok and not (400 <= resp.status_code < 500 and resp.json().get('errorCode')):
            try:
                resp.raise_for_status()
            except HTTPError:
                _logger.error(resp.text)
                credibanco_error = resp.json().get('errorMessage')
                error_msg = " " + ("%s" % credibanco_error)
                raise ValidationError(error_msg)
        return resp.json()

    def _credibanco_reference(self,order):
        o=order['orderNumber'].split('-')
        self._cr.execute("""
        select transaction_id from sale_order o, sale_order_transaction_rel r where r.sale_order_id=o.id and name=%s order by transaction_id desc limit 1
        """,[o[0]])
        transaction_id = self._cr.fetchone()
        self._cr.execute("""
        update payment_transaction set reference2=%s where id=%s
        """,[order['orderId'],transaction_id])

        #self._cr.execute("""
        #update sale_order set name=%s where name=%s
        #""",[order['orderId'],o[0]])

        return {'formUrl':order['formUrl']}

    def credibanco_form_generate_values(self, tx_values):
        _logger.info('form_values')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tx = self.env['payment.transaction'].search([('reference', '=', tx_values.get('reference'))])
        # payulatam will not allow any payment twise even if payment was failed last time.
        # so, replace reference code if payment is not done or pending.
        
        ##if tx.state not in ['done', 'pending']:
        ##    tx.reference = str(uuid.uuid4())
        jParam={"installments":1,"VA.amount":0}
        environment = 'prod' if self.state == 'enabled' else 'test'
        credibanco_values = {
            'userName': self.userName,
            'password': self.password,
            'orderNumber': tx_values['reference'],
            'amount': int(float_round(tx_values['amount'] * 100, 2)),
            'language': tx_values.get('partner_lang', '').upper()[0:2],
            'returnUrl': urls.url_join(base_url, CredibancoController._notify_url),
            'failUrl': urls.url_join(base_url, CredibancoController._cancel_url),
            'api_url': self._get_credibanco_urls(environment)
            #'acquire_id': self.acqui
            #description= 'Descripcion',
        }
        
        tx_values.update(credibanco_values)
        return tx_values

    
class PaymentTransactionCredibanco(models.Model): 
    _inherit = 'payment.transaction'
    @api.model
    def form_feedback(self, data, acquirer_name):
        _logger.info('feedback')
        _logger.info(data)        
        _logger.info('tansaction <+++++++++++')
        if data.get('orderId') and acquirer_name == 'credibanco':
            transaction = self.env['payment.transaction'].search([('reference', '=', data['oldId'])])
            _logger.info('tansaction <-------------')
            _logger.info(transaction)
        # data['orderId']=query_res[0]
        
        self._cr.execute("""
        update payment_transaction set reference=%s,reference2=%s where reference=%s
        """,[data.get('oldId'),data.get('orderId'),data.get('orderId')])

        _logger.info('Cambiado....')
        _logger.info(data)
        return super(PaymentTransactionCredibanco, self).form_feedback(data, acquirer_name)

    @api.model
    def _credibanco_form_get_tx_from_data(self, data):
        _logger.info('from_data')
        _logger.info(data)
        reference = data.get('orderId')
        
        if not reference:
            error_msg='No reference'
            raise ValidationError(error_msg)
        tx = self.search([('reference', 'ilike', reference)])
        if not tx:
            error_msg = (_('Credibanco: no order found for reference %s') % reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('Credibanco: %s orders found for reference %s') % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def _credibanco_form_validate(self, data):
        self.ensure_one()
        _logger.info('validate')
        _logger.info(data)
        page=data.get('page')
        
        _logger.info('OrderID: %s',data.get('orderId'))
        mensaje=''
        if data.get('errorCode') :
            mensaje=data.get('errorCode')+':'+data.get('errorMessage')
        res = {
            'acquirer_reference': data.get('oldId'),
            'state_message': mensaje,
        }
        _logger.info(res)
        if page=='cancel':
            res.update(state='cancel')
            self._set_transaction_cancel()
            return self.write(res)
        if page=='success':
            res.update(state='done', date=fields.Datetime.now())
            self._set_transaction_done()
            self.write(res)
            self.execute_callback()
            return True

    