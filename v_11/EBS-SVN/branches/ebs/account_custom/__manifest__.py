# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Accounting and Financial Custom',
    'author' : 'NCTR',
    'category': 'Accounting',
    'description': """
     Adding the following Features:
    1. Partner & Tax Customization.
    """,
    'website': 'http://www.nctr.sd',
    'depends' : ['base_custom', 'account_cancel', 'account_invoicing', 'account_parent', 'account_fiscalyear', ],
    'data': [
        'security/account_custom_security.xml',
        'views/account_custom.xml',
        'views/chart_account_report.xml',
        'views/chart_account_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
