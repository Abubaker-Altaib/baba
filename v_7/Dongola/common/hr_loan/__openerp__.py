# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Loans',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employee Loans',
    'description': """
Human Resources Management
==========================


    """,

    
   'depends': ['hr','hr_custom','hr_payroll_custom'],
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_loan_request_view.xml',
        'wizard/hr_loan_wizard_view.xml',
        'wizard/hr_loan_wizard_report_view.xml',
        'wizard/hr_loan_transfer.xml',
        'report/hr_loan_report_view.xml',
        'hr_loan_view.xml',
        'company_view.xml',
        'hr_employee_loan_view.xml',
        'hr_loan_arc.xml',
        'hr_loan_workflow.xml',
        'hr_loan_configuration_workflow.xml',
        'loan_sequence.xml',
        
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
