# -*- coding: utf-8 -*-
{
    "name": "Product Dynamic Codes",
    "version": "15.0.1.0.1",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/15.0/product-dynamic-codes-638",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "product"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/cron.xml",
        "views/product_code_position.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/res_config_settings.xml"
    ],
    "assets": {},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to flexibly and automatically update product internal references",
    "description": """
For the full details look at static/description/index.html
- As soon the app is installed, current products' references might be re-calculated

* Features * 

- Automatic product references based on rules



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "39.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=105&ticket_version=15.0&url_type_id=3",
}