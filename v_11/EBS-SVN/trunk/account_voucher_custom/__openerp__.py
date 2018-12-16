# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Check for Accounting Voucher",
    "version": "9.0.shamil v4, wafi v2",
    "category": "Accounting & Finance",
    "description": """
Connecting Accounting Voucher with budget confirmations
=======================================================
each voucher line with analytic account must approved from managerial accounting department before
closing & creating journal entry for voucher.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_voucher", "account_budget_custom"],
    "data": [
        #"views/account_voucher_workflow.xml",
        "views/account_voucher_view.xml",
    ],
    "test": [
        #"test/account_voucher.yml"
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
