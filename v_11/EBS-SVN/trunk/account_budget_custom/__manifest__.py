# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Management",
    "version": "shamil v4, wafi v2",
    "category": "Generic Modules/Accounting",
    "description": """
Budget Management
================================
This module allows accountants to manage analytic and budgets operations.
    * Entering Fisacal Years & Periods Budget. also provides some budget operations (increasing, transfering,...)
    * Allow printing three types of Budget Reports:

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget", "base_custom","account_fiscalyear"],
    "data": [
        "data/sequence.xml",
        "security/account_budget_security.xml",
        "security/ir.model.access.csv",
        "views/account_budget_view.xml",
        #"views/account_budget_custom_report.xml",
        "views/account_budget_operation_view.xml",
        #"views/report_budgetreport.xml",
        "views/account_budget_confirmation_view.xml",
        "report/account_budget_report_view.xml",
        "report/print_budget_template.xml",
        "report/Print_Budget_report.xml",
        "wizard/budget_comparsion_wizard_view.xml",
        "report/budget_comparsion_template.xml"

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
