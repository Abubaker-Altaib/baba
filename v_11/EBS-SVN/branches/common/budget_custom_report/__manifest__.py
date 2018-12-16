# -*- coding: utf-8 -*-
{
    'name': "budget_custom_report",

    'summary': """
        Custom Budget Report """,

    'description': """
        Custom Budget Reports To show analytics with their parents and also show their budgetry positions
    """,

    'author': "NCTR",
    'website': "http://www.nctr.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_budget_custom'],

    # always loaded
    'data': [
        'wizard/budget_main_view.xml',
        'wizard/budget_comparison_view.xml',
        'templates/budget_main_template.xml',
        'templates/budget_comparison_template.xml',
    ],

}
