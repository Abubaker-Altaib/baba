# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Payroll Custom',
    'version': 'EBS 1.0',
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

    'depends': ['hr_payroll','hr_contract_custom'],

    'data': [
        # 'security/ir.model.access.csv',
        #'views/hr_share.xml',
        #'views/templates.xml',
        #'views/hr_payroll.xml',
        #'views/hr_tax.xml',
        'views/hr_payslip_views.xml',
		'views/hr_employee_views.xml',
    ],
    'atuo_install':False,
}
