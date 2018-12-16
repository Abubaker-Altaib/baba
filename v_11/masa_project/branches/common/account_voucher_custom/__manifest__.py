# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Voucher Custom",
    "version": "Maknoun",
    "category": "Accounting & Finance",
    "description": """
Connecting Accounting Voucher with budget confirmations
=======================================================
each voucher line with analytic account must approved from managerial accounting department before
closing & creating journal entry for voucher.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_voucher", "account_budget_custom","account_check_printing_custom"],
    "data": [
        "security/account_voucher_custom_security.xml",
        "wizard/voucher_reject_reason_wizard.xml",
        "views/voucher_reject_reason_template.xml",
        "views/account_voucher_view.xml",
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "sequence/sequence.xml",
        'report/account_voucher_custom_report.xml',
        'report/exchange_request_template.xml',
        'report/report_payment_voucher_template.xml',
        ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
