# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Account Invoice Custom",
    "version" : "shamil-1.0",
    "author" : "NCTR",
    "category": 'Generic Modules/Accounting',

    'init_xml': [],
    "depends" : ['account_custom'],
    'data': [
        'account_invoice_view.xml',
        'account_report.xml'
    ],
   'test': [
        'test/account_invoice.yml',
    ],
   
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
