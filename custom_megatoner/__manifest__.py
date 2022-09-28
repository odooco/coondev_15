# -*- coding: utf-8 -*-
{
    'name': 'Modificaciones Megatoner',
    'version': '15.0',
    'author': 'Coondev - Daniers D.',
    'license': 'OPL-1',
    'maintainer': 'Coondev',
    'website': 'https://coondev.com',
    'summary': ' ',
    'description': """
Coondev megatoner customization
======================
  """,
    'depends': ['base','account','account_accountant','account_online_synchronization','product','stock','contacts','l10n_latam_base','product_category_codes'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/product_brand_megatoner.xml',
        'data/product_color_megatoner.xml',
        'data/calendar_day_megatoner.xml',
        'views/account_bank_statement.xml',
        'views/account_move.xml',
        'views/sale_view.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/product_category.xml',
        'views/product_product.xml',
        'views/product_brand_megatoner.xml',
        'views/product_color_megatoner.xml',
        'views/calendar_day_megatoner.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
