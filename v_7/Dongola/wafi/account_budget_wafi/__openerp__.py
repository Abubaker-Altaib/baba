# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Management Wafi",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """
    This module modify budget workflow to match government process.
    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget_custom"],
    "data": [
        "account_budget_view.xml",
        "account_budget_workflow.xml",
        "account_budget_operation_view.xml",
    ],
    "test": [
             "test/account_fiscalyear_budget.yml",
             "test/account_budget.yml"
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
