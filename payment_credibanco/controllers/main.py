# -*- coding: utf-8 -*-
import pprint
import logging
import json
import requests
import re
from werkzeug import urls, utils

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)


class CredibancoController(http.Controller):
    _notify_url = '/payment/credibanco/success'
    _cancel_url = '/payment/credibanco/cancel'

    @http.route(['/payment/credibanco/success/', '/payment/credibanco/cancel'], type='http', auth='public')
    def credibanco_result(self, **kwargs):
        r=re.search('(\/cancel\?)',http.request.httprequest.full_path)
        
        kwargs['page']='success'
        if(r):
            kwargs['page']='cancel'
        
        request._cr.execute('''
        select o.name from payment_transaction t, sale_order_transaction_rel r, sale_order o where t.reference2=%s and r.transaction_id=t.id and o.id=r.sale_order_id
        ''',[kwargs['orderId']])
        query_res = request._cr.fetchone()
        kwargs['oldId']=kwargs['orderId']
        kwargs['orderId']=query_res[0]
        _logger.info('req: %s',kwargs)
        
        request.env['payment.transaction'].sudo().form_feedback(kwargs, 'credibanco')
        return utils.redirect('/payment/process')

    @http.route(['/payment/credibanco/api'], type='json', method='POST', auth='public', csrf=False)
    def credibanco_api(self, **kwargs):
        _logger.info('pay-----------------')
        
        acquirer_id = int(kwargs.get('acquirer_id'))
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        res=acquirer._credibanco_request(kwargs)
        res['orderNumber']=kwargs['orderNumber']
        res['acquirer_id']=acquirer_id
        return res 

    @http.route(['/payment/credibanco/reference'], type='json', method='POST', auth='public', csrf=False)
    def credibanco_reference(self, **kwargs):
        
        acquirer_id = int(kwargs.get('acquirer_id'))
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        res=acquirer._credibanco_request(kwargs)
        _logger.info(res.get('orderId'))
        acquirer._credibanco_reference(kwargs)
        return {'errorCode':1,'errorMessage':'xxxx'} #werkzeug.utils.redirect('/payment/process')
