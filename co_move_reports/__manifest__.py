###############################################################################################
#
# Daniers Diaz  - Julian Bocanegra
# Odoo Dev        Odoo Consulting
# 
# Bogotá,Colombia
#
#
###############################################################################################

{
    'name': 'Reportes de Asientos Contables',
    'version': '15.0.0.0',
    'author': "Coondev S.A.S",
    'contributors': ['Luis Felipe Paternina','M. Daniers C. Diaz.'],
    'website': "www.coodev.com",
    'category': 'reports',
    'images': ['static/description/icon.png'],
    'depends': [
        'account',
        'account_accountant',
        'base',
    ],
    'data': [
        'reports/account_report.xml',
    ],
    'installable': True
}
