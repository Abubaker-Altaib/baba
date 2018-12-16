# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial Arabic Reports",
    "author" : "NCTR",
    "category": 'Generic Modules/Accounting',
    "description": """Financial and accounting Arabic Reports""",
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    "depends" : ["account_custom"],
    'data': [
        'account_report.xml',
        'wizard/account_report_general_ledger_view.xml',
        'wizard/account_report_partner_balance_view.xml',
        'wizard/account_report_account_balance_view.xml',
        'wizard/account_report_partner_ledger_view.xml',
        'wizard/account_report_account_statement_view.xml',
        'data/report_audit.xml'
    ],
    "test" : [
        'test/account_arabic_reports.yml',
    ],
       "demo_xml" : [
    ],
        'installable': True,
        'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
