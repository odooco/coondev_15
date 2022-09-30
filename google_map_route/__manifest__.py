{
    'name': 'Google Map Integration With Odoo',
    'version': '15.0.0.2',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragmatic.com',
    'maintainer': 'sales@pragtech.co.in',
    'category': 'Web',
    'description': """
Pragmatic has developed module which provides the integration between Google map and Odoo. 
==========================================================================================
Advantages:-
-------------
    * Shows the customer address on google map with pinpoint on Customer form in Odoo.
    * Shows the route between login user address and partner address on Sales Order form
    * Shows the route between login user address and partner address on delivery order form
    * Autocomplete address / Suggestion.
    
<keywords>
Google map with Odoo
google map
maps
""",
    'depends': [
        'base_setup',
        'base_geolocalize',
        'sale_management',
        'contacts',
        'sale_stock',
        'stock',
    ],
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/sale_map_view.xml',
        'views/delivery_order_map_view.xml'
    ],

    'assets': {

        'web.assets_backend': [
            'google_map_route/static/src/scss/web_maps.scss',
            'google_map_route/static/src/scss/web_maps_mobile.scss',
            'google_map_route/static/src/js/view/map/map_model.js',
            'google_map_route/static/src/js/view/map/map_controller.js',
            'google_map_route/static/src/js/view/map/map_renderer.js',
            'google_map_route/static/src/js/view/map/map_view.js',
            'google_map_route/static/src/js/view/view_registry.js',
            'google_map_route/static/src/js/view/form/form_controller.js',
            'google_map_route/static/src/js/view/form/form_view.js',
            'google_map_route/static/src/js/fields/relational_fields.js',
            'google_map_route/static/src/js/widgets/utils.js',
            'google_map_route/static/src/js/widgets/gplaces_autocomplete.js',
            'google_map_route/static/src/js/widgets/fields_registry.js',
        ],

        'web.assets_qweb': [
            'google_map_route/static/src/xml/widget_places.xml',
        ],
    },

    'images': ['static/description/Animated-googlemap-integration.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=310&name=support-odoo-google-map-integration',
    'uninstall_hook': 'uninstall_hook',
    'price': 30,
    'currency': 'EUR',
    'license': 'OPL-1',
    'active': False,
    'installable': True,
}
