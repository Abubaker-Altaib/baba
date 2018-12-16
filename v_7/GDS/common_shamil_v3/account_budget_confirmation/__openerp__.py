# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Budget Confirmation Management',
    'version': 'wafi-1.0',
    'category': 'Generic Modules/Accounting',
    'description': """ 
    This module for excluse the expense amount (voucher, ratification, purchase, ..)
    from specific Budget as confirmed amount, till creating its Jornal Entry and transmute 
    this amount to actual expense.""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account_budget_custom'],
    'init_xml': [],
    'data': [
        'data/sequence.xml',
        'account_budget_view.xml',
        'account_budget_workflow.xml',
        'security/ir.model.access.csv',
        'report/account_report.xml',
    ],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
