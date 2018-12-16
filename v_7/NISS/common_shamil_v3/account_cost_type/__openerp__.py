# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    'name': 'Account Cost Type',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """
""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account_custom', 'account_voucher_custom'],
    'init_xml': [],
    'update_xml': [

        'account_cost_type_view.xml',
        'wizard/account_cost_type_balance_report.xml',
        'wizard/account_report_cost_type_ledger_view.xml',

   
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
