#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll custom',
    'category': 'Human Resources',
    'sequence': 38,
    'summary': 'Manage your employee payroll records',
    'description': "",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    'depends': [
        'hr_payroll','hr_recruitment','hr_custom'
    ],
    'data': [
        'security/hr_payroll_custom_security.xml',
        'data/payroll_suspended_unsuspend_data.xml',
        'views/hr_promotions_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views .xml',
        'views/hr_payslip_views.xml',
        "views/employee_medical_insurance.xml",
    ],
}
