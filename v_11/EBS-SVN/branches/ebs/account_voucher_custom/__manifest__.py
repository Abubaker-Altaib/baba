# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Sale & Purchase Vouchers Custom',
    'version': '1.1',
    'category': 'Accounting',
    'description': """
Additional features added to Account Voucher:
    1. Connecting Accounting Voucher with budget confirmations
    2. Connect Pay later with payment (Register Payment)
    3. Add Installment to voucher
    4. Can apply to multi currency
    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account_voucher', 'account_budget_custom'],
    'data': [
        #'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
        'views/account_payment_view.xml',
        'views/account_voucher_view.xml',
        # 'views/ratification_claim.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
