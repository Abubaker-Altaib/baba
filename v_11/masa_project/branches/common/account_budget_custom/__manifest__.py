# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Custom",
    "version": "1.1",
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
    "depends": ["account_budget","account_custom"],
    "data": [
        "data/sequence.xml",
        "security/account_budget_security.xml",
        "security/ir.model.access.csv",
        "views/account_budget_view.xml",
        "views/account_budget_operation_view.xml",
        "views/account_budget_confirmation_view.xml",
        "views/account_fiscalyear_budgte_view.xml",
        "views/fiscalyer_budget_config_view.xml",
        "sequence/account_budget_custom_seq.xml",
        "report/account_budget_report_view.xml",
        "report/budget_confirmation_report_view.xml",
        "report/balancing_certification_notice_report.xml",
        "report/balancing_certification_notice_template.xml",
        "report/print_budget_template.xml",
        "report/Print_Budget_report.xml",
        "report/field_budget_report.xml",
        "report/field_budget_tempelate.xml",

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
