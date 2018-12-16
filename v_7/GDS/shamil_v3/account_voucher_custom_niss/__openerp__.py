# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Account Voucher Custom NISS",
    "version" : "shamil-1.0",
    "author" : "NCTR",
    "category": 'Generic Modules/HR/Payroll',

    'init_xml': [],
    "depends" : ['account_voucher_custom','account_check_writing_custom','account_voucher_multi_taxes','hr_custom'],
    'data': [
        'security/account_voucher_workflow_security.xml',
        'security/account_move_security.xml',
        'account_voucher_custom_niss.xml',
        'account_report_niss.xml',
        'account_move_view.xml',
        'res_partner_view.xml',
        'account_custody_view.xml',
        'security/res_partner_security.xml',
        'account_voucher_workflow.xml',

        'wizard/account_close_period.xml',
        'wizard/account_custody_change_partner.xml',


    ],
   'test': [],
   
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
