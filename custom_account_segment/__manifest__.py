# -*- coding: utf-8 -*-
{
    'name': 'Reclasificaciones',
    'version': '15.0',
    'author': 'Juan De Dios',
    'license': 'OPL-1',
    'summary': ' ',
    'description': """
 customization Account Segmentation
======================
  """,
    'depends': ['base','account','sale','account_accountant','pos_sale_report'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/account_journal.xml',
        'views/account_move_pos_views.xml',
        'views/res_company.xml',
        'reports/pos_invoice_report.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
