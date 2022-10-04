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
    'depends': ['base','account','account_accountant'],
    'data': [
        #'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/account_journal.xml',
        'views/res_company.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
