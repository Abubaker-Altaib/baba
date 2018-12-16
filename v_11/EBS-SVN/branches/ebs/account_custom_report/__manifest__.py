# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial Custom Report",
    "author" : "NCTR",
    "category": "Accounting",
    "description": """
     Adding the following Features:
    1. Partner & Tax Customization.
    """,
    "website": "http://www.nctr.sd",
    "depends" : ['account_custom','account_budget_custom'],
    "data": [
        #'views/account_custom.xml',
        #'security/account_custom_security.xml',
        'templates/trial_balance_template.xml',
        #'templates/analytic_budget_report_template.xml',
        'templates/partner_ledger_report_template.xml',
        'templates/partner_balance_report_template.xml',
        
        'report/account_statement.xml',
        'report/account_statement_action.xml',
        'report/report_trialbalance_view.xml',
        'wizard/account_statement_view.xml',
        'wizard/account_wizard_trial_balance_view.xml',
        'wizard/trial_balance_d_wizard_view.xml',
        #'wizard/analytic_budget_report_wizard_view.xml',
        
        #'templates/account_partner_balance.xml',
        'report/account_journalEntry_view.xml',
        'report/account_journalEntry_action.xml',
        'wizard/account_debt_reconstruction_view.xml',
        'wizard/partner_leadger_report_wizard_view.xml',
        'wizard/partner_balance_report_wizard_view.xml',
        #'wizard/account_report_common_view.xml',
        #'wizard/account_report_partner_balance_view.xml',
        'report/account_debt_reconstruction_action.xml',
        'report/account_debt_reconstruction_view.xml',


    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
