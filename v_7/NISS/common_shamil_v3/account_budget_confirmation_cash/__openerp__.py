# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Budget Confirmation Cash Management',
    'version': 'wafi-1.0',
    'category': 'Generic Modules/Accounting',
    'description': """ 
    This module for excluse the expense amount (voucher, purchase, ..)
    from specific Budget as confirmed amount, till creating its Jornal Entry and transmute 
    this amount to actual expense.""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account_budget_cash','account_budget_confirmation'],
    'data': [
        'account_budget_view.xml',
    ],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
