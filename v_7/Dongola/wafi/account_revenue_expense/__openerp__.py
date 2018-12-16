# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Revenues & Expense Management ",
    "version" : "wafi-1.0",
    "depends" : ["account_voucher_wafi","account_check_writing_custom"],
    "author" : "NCTR",
    "description": """
Managing revenues & expenses by:
---------------------------------------
1. Revenue distribution to feed cash budget.
2. Scheduling expense payments base on their priorities.
    """,
    "website" : "http://www.nctr.sd",
    "category" : "Accounting & Finance",
    "data" : [
        "account_revenue_expense_sequence.xml",
        "account_revenues_view.xml",
        "security/ir.model.access.csv",
        "security/account_revenue_expense_security.xml",
        #"data/account_revenues.xml",
        "account_revenue_expense_workflow.xml",
    ],
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

