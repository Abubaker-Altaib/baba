# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Cash Budget Management",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """This module allows accountants to manage Cash budgets operations.

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget_custom"],
    "init_xml": [],
    "data": [
        "account_budget_view.xml",
        "account_budget_operation_view.xml",
    ],
    "test": [
    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
