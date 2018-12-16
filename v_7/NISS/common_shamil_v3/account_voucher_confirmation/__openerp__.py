# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Check for Accounting Voucher",
    "version": "wafi-1.0",
    "category": "Accounting & Finance",
    "description": """
Connecting Accounting Voucher with budget confirmations
=======================================================
each voucher line with analytic account must approved from managerial accounting department before
closing & creating journal entry for voucher.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_voucher_custom","account_budget_confirmation"],
    "data": [
        "account_voucher_workflow.xml",
        "account_voucher_view.xml",
    ],
    "test": [
        "test/account_voucher.yml"
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
