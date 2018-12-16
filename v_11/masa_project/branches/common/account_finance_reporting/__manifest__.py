# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Account Financial Reports",
    "version": "Maknoun",
    "category": "Generic Modules/Accounting",
    "description": """

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account", "account_parent","base_custom"],
    "data": [
        
        "views/report_trialbalance.xml",
        "views/account_report.xml",
        "views/report_account_statement.xml",
        "views/report_journal.xml",
        "views/report_analytic_statement .xml",
        "views/account_financial_report.xml",
        "views/report_financial.xml",
        "views/financial_report_data.xml",
        'views/journal_items_view.xml',
        "wizard/account_report_trial_balance_view.xml",
        "wizard/account_statement_view.xml",
        "wizard/account_report_print_journal_view.xml",
        "wizard/account_report_analytic_statement.xml",
        "wizard/account_financial_report_view.xml",

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
