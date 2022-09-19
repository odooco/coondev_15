# -*- coding: utf-8 -*-

{
    'name': 'Credibanco',
    'author': "Jose Reyes",
    'website': "http://www.fenalco.com.co",
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: credibanco Implementation',
    'license': 'OPL-1',
    'version': '1.0',
    'description': """Credibanco Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_credibanco_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
