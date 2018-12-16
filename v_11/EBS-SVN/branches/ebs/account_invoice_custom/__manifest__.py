# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Account Invoice Custom',
    'version': '1.0',
    'author' : 'NCTR',
    'category': 'Accounting',
    'description': """
     Adding the following Features:
        1. Invoice Connection with budget confirmations
        2. Add Deferred Revenue to Invoice
        3- Add Direct Revenue to Invoice "create payment automatically in case of pay now"
    """,
    'website': 'http://www.nctr.sd',
    'depends' : ['account_budget_custom'],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
