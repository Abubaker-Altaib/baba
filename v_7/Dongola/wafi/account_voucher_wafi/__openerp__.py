# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Business Process for WAFI Accounting Voucher',
    'author': 'NCTR',
    'version': 'wafi-1.0',
    'category': 'Generic Modules/Accounting',
    'description': """
Additional features added to Account Voucher:
--------------------------------------------------------
1. Allow adding schedule payments feature.
2. Modify account balance computation.
3. Modify Voucher Workflow.
    """,
    'website': 'http://www.nctr.sd',
    'depends': ['account_custom_wafi','account_voucher_confirmation'],
    'data': [
        'wizard/account_fiscalyear_cancel_payment_wizard.xml',
        'account_account_view.xml',
        'voucher_direct_sales_purchase_view.xml',
        'voucher_bank_cash_view.xml',
        'account_voucher_workflow.xml',
        'account_report.xml',
    ],
    'installable': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:







