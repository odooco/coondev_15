odoo.define(custom_rutes.import', function (require)
{
   "use strict";
   var core = require('web.core');
   var ListController = require('web.ListController');
   ListController.include({
       renderButtons: function($node)
       {
           this._super.apply(this, arguments);
               if (this.$buttons)
               {
                   let import_button = this.$buttons.find('.import_data_button');
                   import_button && import_button.click(this.proxy('import_button')) ;
               }
       },
       import_button: function ()
       {
           this.do_action({
               type: "ir.actions.act_window",
               name: "enrutar",
               res_model: "enrute",
               views: [[false,'form']],
               target: 'new',
               view_mode : 'form'
           });
return { 'type': 'ir.actions.client','tag': 'reload', }
       }
   });
})