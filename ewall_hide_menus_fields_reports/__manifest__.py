# -*- coding: utf-8 -*-
{
    'name': "Hide Menu, Hide Fields and Hide Reports V15",

    'summary': """
    Hide/Invisible Any Menu, Sub-Menu, Field, Report From Any User Or Any Group And Its User
        """,

    'description': """
        Hide Any Menu, Sub-Menu And Report From User Configuration On User Form View
        Hide Any Menu, Sub-Menu And Report From User Configuration On Menu Form View
        Hide Report From Menu, User Configuration On Report Form View
        Hide, Set Readonly Any Field From Any Group And Its Users Configuration On Models Form View.
        For Security Reason We Do Not Apply Above Configuration On Super User(Administrator).
    """,

    'author': "EWall Solutions Pvt. Ltd.",
    'website': "https://www.ewallsolutions.com",
    'company': "Ewall Solutions Pvt. Ltd.",
    'support':'support@ewallsolutions.com',
    'currency':'USD',
    'price':'10.00',
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.1.0.1',

    # Any module necessary for this one to work correctly
    'depends': ['base'],

    # Always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ir_action_reports.xml',
        'views/ir_model.xml',
        'views/res_groups.xml',
        'views/res_users.xml',
    ],
    'images': [
        'static/description/images/banner.jpg',
    ],
}
