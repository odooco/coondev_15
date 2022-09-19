console.log('antes');
odoo.define('payment_authorize.payment_form', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    var core = require('web.core');
    var PaymentForm = require('payment.payment_form');
    
    var _t = core._t;
    
    PaymentForm.include({
        
        _createCredibanco:function(ev,$checkedRadio){
            ev.preventDefault();
            console.log('_createCredibanco');
            var form = this.el;
            var checked_radio = this.$('input[type="radio"]:checked');
            var self = this;
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }
            checked_radio = checked_radio[0];

            // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = false;
            if (this.isNewPaymentRadio(checked_radio)) {
                acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
            } else {
                acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
            }
            var inputs_form = $('input', acquirer_form);
            var ds = $('input[name="data_set"]', acquirer_form)[0];
            var form_data = this.getFormData(inputs_form);
            var wrong_input = false;
            var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
            this.disableButton(button);
            console.log(form_save_token);
            console.log(self.options.orderId);
            this._rpc({
                route: '/shop/payment/transaction/',
                params: {
                    'acquirer_id': parseInt(acquirer_id),
                    'save_token': form_save_token,
                    'access_token': self.options.accessToken,
                    'success_url': self.options.successUrl,
                    'error_url': self.options.errorUrl,
                    'callback_method': self.options.callbackMethod,
                    'order_id': self.options.orderId,
                },
            }).then(function (result) {
                var object = $('<div/>').html('<div>'+result+'</div>').contents();
                    
                var paramx={
                    'userName': object.find('input[name="userName"]').val(),
                    'password': object.find('input[name="password"]').val(),
                    'amount': object.find('input[name="amount"]').val(),
                    'language': object.find('input[name="language"]').val(),
                    'orderNumber': object.find('input[name="orderNumber"]').val(),
                    'returnUrl': object.find('input[name="returnUrl"]').val(),
                    'failUrl': object.find('input[name="failUrl"]').val(),
                    'api_url':object.find('input[name="api_url"]').val(),
                    'acquirer_id': acquirer_id,
                };
                self._rpc({
                    route: '/payment/credibanco/api',
                    params: paramx,
                }).then(function(result){
                    if(result.hasOwnProperty('errorCode')){
                        self.enableButton(button);
                        return self.displayError(_t('Server Error'), result['errorMessage']);
                    }else{
                        return {'orderNumber':result['orderNumber'],'acquirer_id':result['acquirer_id'],'orderId':result['orderId'],'formUrl':result['formUrl']};
                    }
                }).then(function(r){
                    if(r != undefined){
                        self._rpc({
                            route: '/payment/credibanco/reference',
                            params:r
                        }).then(function(result){
                            window.location=r['formUrl']
                        });
                    }
                    
                });
                
            });
            
            return ;
        },
        /**
         * @override
         */
        updateNewPaymentDisplayStatus: function () {
            var $checkedRadio = this.$('input[type="radio"]:checked');

            if ($checkedRadio.length !== 1) {
                return;
            }

            //  hide add token form for authorize
            if ($checkedRadio.data('provider') === 'authorize' && this.isNewPaymentRadio($checkedRadio)) {
                this.$('[id*="o_payment_add_token_acq_"]').addClass('d-none');
            } else {
                this._super.apply(this, arguments);
            }
        },
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        payEvent: function (ev) {
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');
            console.log('click1');
            console.lo
            // first we check that the user has selected a authorize as s2s payment method
            if ($checkedRadio.length === 1 && $checkedRadio.data('provider') === 'credibanco') {
                this._createCredibanco(ev, $checkedRadio);
            } else {
                this._super.apply(this, arguments);
            }
        },
        /**
         * @override
         */
        addPmEvent: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');
            console.log('click2');
            // first we check that the user has selected a authorize as add payment method
            if ($checkedRadio.length === 1 && $checkedRadio.data('provider') === 'credibanco') {
                this._createCredibanco(ev, $checkedRadio, true);
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});    