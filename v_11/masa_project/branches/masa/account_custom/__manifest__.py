# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name' : 'Accounting and Financial Custom',
    'version': '1.1',
    'author' : 'NCTR',
    'category': 'Accounting',
    'description': '''
     Adding the following Features:
    1. Partner & Tax Customization.
    ''',
    'website': 'http://www.nctr.sd',
    'depends' : ['account', 'account_cancel', 'base_custom'],
    'data': [
        'security/account_security.xml',
        'views/account_payment_view.xml',
        'views/account_view.xml',
        #'views/partner_view.xml',
        'views/account_analytic_view.xml',
        'views/chart_account_report.xml',
        'views/chart_account_report_template.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
