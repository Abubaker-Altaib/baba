# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Check Printing Custom',
    'version' : '1.0',
    'summary': 'Check printing Custom',
    'author' : 'NCTR',
    'website': 'http://www.nctr.sd',
    'description' : """account check printing custom""",
    'depends' : ['account_check_printing','account_voucher_custom'],
    'data': [
        'data/data.xml',
        'views/account_view.xml',
        'wizard/account_check_print_wizard_view.xml',
        'wizard/account_check_cancel_view.xml',
        'report/account_check_printing_report.xml',
        'report/print_check_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
