# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Accounting Reports',
    'version' : '1.1',
    'summary': 'Create financial reports',
    'sequence': 30,
    'description': """
Financial Reports
====================
Create financial reports
    """,
    'category': 'Accounting', 
    'depends' : ['base','base_setup', 'account', 'analytic', 'report', 'web_planner','account_accountant', 'l10n_su_microfinance'],
    'data': [   
        'views/account_financial_report.xml',
        'views/report_cashflow.xml',
        'views/accounting_reports_report.xml',
        'views/report_journal_entry.xml',
	'views/report_payment.xml',
        'views/report.xml',
        'views/report_trialbalance.xml',
	'views/report_generalledger.xml',
	'views/report_partnerledger.xml',
        'views/report_account_statement.xml',	
        'views/cash_flow_data.xml',
        'views/change_owner_equity.xml',
        'wizard/account_cashflow_report_view.xml',
        'wizard/account_statement_view.xml',
    ],
   
    
    'auto_install': False,
    'installable': True,
    'application': True,

}
