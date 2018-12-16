# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name' : 'Overtime Management',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """ 
Manage overtime plan and pay
=====================================

    """,
    'author' : 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends' : ['hr_payroll_custom', 'account_voucher_custom'],
    'data': [
        'views/views.xml',
    ],
    'atuo_install':False,
}

