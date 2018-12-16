# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Account Liquidity Custody",
    "version" : "shamil-1.0",
    "author" : "NCTR",
    "category": 'Generic Modules/Accounting/Custody',

    'init_xml': [],
    "depends" : ['account_voucher_custom'],
    'data': [
        'account_liquidity_custody_sequence.xml',
        'account_liquidity_custody_group.xml',
        'wizard/account_liquidity_custody_wizard.xml',
        'account_liquidity_custody.xml',
        'account_liquidity_custody_workflow.xml',
        
    ],
   'test': [],
   
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
