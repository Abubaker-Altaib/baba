# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': "zakat_base",
    'author': "NCTR",
    'website': "http://www.nctr.sd",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': 'Zakat V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'account_invoicing', 'account_voucher'],
    #'demo': ['demo/demo.xml'],
    'css': ['static/src/css/styles.css'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/zakat_base_security.xml',
        'views/zakat_base_view.xml',
        'views/zakat_base_config_view.xml',
        'views/custom_theme.xml',
        'views/app_icons_custom.xml',
        'sequence/zakat_base_seq.xml',
        'report/report_action.xml',
       #'report/zakat_base_report_template.xml',

    ],


    'application': True,
    'installable': True,
}
