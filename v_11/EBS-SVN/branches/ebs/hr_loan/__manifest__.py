# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name': 'Loans Request',
    'version': '1.0',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Loans Request',
    'description': """
Human Resources Management
==========================


    """,
    'depends': ['account_custom','account_voucher','hr_payroll_custom'],
    'data': [
        'security/hr_loan_security.xml',
         #'security/ir.model.access.csv',
        #'views/views.xml',
        'views/hr_loan_request_view.xml',
        #'views/templates.xml',
    	#'views/loan_sequence.xml',
    	#'views/company_view.xml',
    	'views/hr_loan_view.xml',
    	'views/hr_loan_arc.xml',
        'views/hr_loan_payment_view.xml',
    ],
    'installable': True,
    'active': True,
    'auto_install': False,
}
