# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Management",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """
Budget Management
================
This module allows accountants to manage analytic and budgets & cash budgets operations.
    * Entering Fisacal Years & Periods Budget. also provides some budget operations (increasing, transfering,...)
    * Allow printing three types of Budget Reports:
    1. Each Period"s Budget and its details (Cost Center Details).
    2. Each Cost Center Budgets as total for specific periods (Cost Center Total).
    3. Each Account Budget as total for specific Cost Center in specific periods (Company Details).
    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["base_custom","account_custom"],
    "init_xml": [],
    "data": [
        "security/account_budget_security.xml",
        "data/sequence.xml",
        'security/ir.model.access.csv',
        "res_config_view.xml",
        "wizard/account_budget_import_wizard_view.xml",
        "account_budget_view.xml",
        "account_budget_workflow.xml",
        "account_budget_operation_view.xml",
        "report/account_report.xml",
        "wizard/account_report_budget_wizard_view.xml",
        "wizard/account_budget_close_wizard_view.xml",
        "wizard/account_budget_cash_flow_wizard_view.xml",
    ],
    "test": [
             "test/account_fiscalyear_budget.yml",
             "test/account_budget.yml"
    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
