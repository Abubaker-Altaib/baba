# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    'name': 'Bank Statment Niss Customization',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """ Give Cancel Button in bank reconcilation to group""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account_bank_statement'],

    'data': [
        'account_bank_statement_view.xml',
        'security/account_bank_statement_security.xml',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:account
