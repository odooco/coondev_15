# -*- coding: utf-8 -*-
{
    "name" : "Acuse de Recibo",
    "author" : "Coondev SAS",
    "email": 'soporte@coondev.com.co',
    "website":'https://coondev.odoo.com/',
    "version":"14.0.1",

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_co_dian_data','l10n_co_e_invoicing'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/factura_proveedor.xml',
    ],
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "COP"
}
