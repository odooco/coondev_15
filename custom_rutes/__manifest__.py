# -*- coding: utf-8 -*-
{
    'name': 'Rutas',
    'version': '15.0',
    'author': 'Coondev - Daniers D.',
    'license': 'OPL-1',
    'maintainer': 'Coondev',
    'website': 'https://coondev.com',
    'summary': ' ',
    'description': """
Coondev megatoner rutas
======================
  """,
    'depends': ['base','sale','web','helpdesk','purchase','custom_megatoner','delivery','base_geolocalize','google_map_route'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/route_activity.xml',
        'views/routes_templates.xml',
        'views/routes.xml',
        'views/res_partner_domiciliary.xml',
        'views/route_activity.xml',
        'views/account_move.xml',
        'views/helpdesk_ticket.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/delivery_carrier.xml',
        'views/enrutar_wizard.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'custom_rutes/static/src/xml/action_button.xml'
        ]
    },
    'installable': True,
}
