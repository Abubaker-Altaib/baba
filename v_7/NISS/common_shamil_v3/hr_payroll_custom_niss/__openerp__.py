# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Payroll Custom NISS',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Details NISS',
    'description': """
Generic Payroll system.
=======================

    * Employee Details
    * Allowances/Deductions
    * Allow to configure Basic/Gross/Net Salary
    * Employee Payslip
    * Monthly Payroll Register
    * Integrated with Holiday Management
    """,
    
    'depends': [
        'report_webkit',
        'hr_payroll_custom',

    ],

    'data': [
       'security/hr_security.xml',
       #'security/ir.model.access.csv',
       'hr_view.xml',
       'hr_employee_view.xml',
       'wizard/payroll_department_view.xml',
       'wizard/payroll_listing_department_view.xml',
       'wizard/employee_salary_suspended.xml',
       'wizard/hr_bonus_candidates_wizard.xml',
       'wizard/hr_promotion_candidates_wizard.xml',
       'wizard/allow_deduct_loan_sum_report_view.xml',


        
  
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
