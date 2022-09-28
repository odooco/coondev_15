# -*- coding: utf-8 -*-
{
    'name': 'Modificaciones - res partner coondev',
    'version': '15.0',
    'author': 'Coondev - Daniers D.',
    'license': 'OPL-1',
    'maintainer': 'Coondev',
    'website': 'https://coondev.com',
    'summary': ' ',
    'description': """
Coondev res partner customization
======================
  """,
    'depends': ['base','sale'],
    'data': [
        'security/res_groups.xml',
        'views/res_partner.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
