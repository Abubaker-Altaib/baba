# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    'name': 'Bank Statment Report',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """ module to change the method of functional field balance_end from equation """,
    'author': 'NCTR',
    'website': 'http://www.openerp.com',
    'depends': ['account_custom','account_bank_statement'],

    'data': [
        'account_bank_statement_report.xml',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:account
