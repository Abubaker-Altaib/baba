# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Business Process for Accounting Voucher',
    'author': 'NCTR',
    'version': 'wafi-1.0',
    'category': 'Generic Modules/Accounting',
    'description': """
Additional features added to Account Voucher:
1. Bank & Cash operations
2. Petty Cash operations
3. Credit/Debit note
    """,
    'website': 'http://www.nctr.sd',
    'depends': ['account_voucher', 'hr', 'account_custom'],
    'data': [
        'security/account_voucher_custom_security.xml',
        'security/ir.model.access.csv',
        'voucher_direct_sales_purchase_view.xml',
        'voucher_bank_cash_view.xml',
        'account_report.xml',
    ],
    'test': [
        'test/account_voucher.yml'
    ],
    'installable': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:







