# -*- coding: utf-8 -*-
{
    'name': "account_asset_custom",

    'summary': """
        add more funtionality to assets
        create main menu for assets
        add custody based on assets""",

    'description': """
        add maintenance and enhancement to assets
        create main menu for assets
        add custody based on assets
    """,

    'author': "NCTR",
    'website': "http://www.nctr.sd",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_asset', 'web_map', 'sale', 'account_voucher_custom', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'data/sequence.xml',
    ],
}
