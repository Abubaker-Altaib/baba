# -*- coding: utf-8 -*-
{
    'name': "Account Code",

    'summary': """
        Account code Module to make codes created automaticly""",

    'description': """
        Account code Module to make restrict to account code size and create it in standard way , like
        if you have accoun 11113 and in configration you set account have size 8 then next child account code will be
         11113001
    """,

    'author': "NCTR",
    'website': "http://www.nctr.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_parent'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/views.xml',
        'views/res_config_settings_views.xml',
        'views/account_account_view.xml'
    ],
    
}
