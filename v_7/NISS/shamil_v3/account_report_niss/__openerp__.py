# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting Report for NISS Project",
    "author" : "NCTR",
    "category": 'Generic Modules/Accounting',
    "description": """Accounting and Financial Report for NISS Project""",
    "version" : "shamil",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    "depends" : ["account_arabic_reports",'account_bank_statment_report',
                 'account_voucher_custom_niss','account_budget_niss'],
    'data': [
        "account_report.xml",
        "wizard/account_report_account_statement_view.xml",
        "wizard/account_report_statement_view.xml",
        "wizard/account_report_account_balance_view.xml",
        "wizard/account_custody_report_view.xml",
        "wizard/account_report_budget_statement_view.xml",
	],
    "test" : [
    ],
  
       "demo_xml" : [
    ],
        'installable': True,
        'active': False,


}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
