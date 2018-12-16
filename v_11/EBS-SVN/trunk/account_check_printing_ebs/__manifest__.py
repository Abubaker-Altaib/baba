# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Check Printing Custom EBS',
    'version' : 'shamil v4, wafi v2',
    'summary': 'Check printing Custom For EBS',
    'author' : 'NCTR',
    'website': 'http://www.nctr.sd',
    'description' : """account check printing custom ebs""",
    'depends' : ['account_check_printing_custom'],
    'data': [
        'views/account_view.xml',
        #'wizard/account_check_print_wizard_view.xml',
        #'wizard/account_check_cancel_view.xml',
        #'views/account_check_printing_report.xml',
        #'views/print_check_view.xml',
        #'views/bank_letter_report.xml',
        #'views/account_bank_letter.xml',
        #'views/print_voucher_check_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
