# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Payroll Custom',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Details, Allowances/Deductions',
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
        'hr_custom',
        'hr_holidays',
        'account_voucher',
        'decimal_precision',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'hr_payroll_data.xml',
        'security/ir.model.access.csv',
        'hr_payroll_data.xml',
        'res_config_view.xml',
        'hr_payroll_view.xml',
        'hr_employee_view.xml',
        'hr_holidays_view.xml',
        'company_view.xml',
        'report/hr_payroll_report.xml',
        'wizard/salary_scale_allow_deduct_view.xml',
        'wizard/allow_deduct_exception_view.xml',
        'wizard/employees_exempt_tax_view.xml',
        'wizard/hr_bonus_candidates_wizard.xml',
        'wizard/payroll_taxes_report.xml',
        'wizard/employees_salary_report.xml',
        'wizard/social_insurrance_report_view.xml',
        'wizard/insurrance_solidarity_report_view.xml',
        'wizard/allowance_deduction_report_view.xml',
        'wizard/payroll_listing_view.xml',
        'wizard/static_emps_by_degree_view.xml',
        'wizard/static_emps_by_dep_view.xml',
        'wizard/salary_scale.xml',
        'wizard/salary_list_total_view.xml',
        'wizard/wizard_promotion_priority_report.xml',
        'wizard/employee_salary_suspended.xml' ,
        #'wizard/payroll_budgets_view.xml',
        'wizard/salary_scale_addition_view.xml',
        'wizard/payroll_report_bank.xml' , 
        #'wizard/allowance_deduction_extra_report_view.xml',
        'scheduler.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
