# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Directory Custom',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Jobs, Departments, Employees Details',
    'description': """
Human Resources Management
==========================


    """,

    
    'depends': ['hr','analytic','account_custom'],
    'data': [
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        "hr_view.xml",
        #"hr_department_view.xml",
        "res_config_view.xml",
        "hr_employee_wkf.xml",
        "hr_employee_se.xml",
        "report/hr_report.xml",
        "wizard/hr_employee_report.xml",
        "wizard/hr_report_jobs.xml",
        "hr_employee_qualification_wkf.xml",
        'hr_employee_family_wkf.xml',
        'res_company_view.xml',
        'hr_process_view.xml',
        'hr_view_extra.xml',
        #'wizard/wizard_delegation_report.xml',
        'wizard/wizard_promotion_report.xml',
        'wizard/wizard_transfer_report.xml',
        'hr_process_workflow.xml',
        'hr_delegation_workflow.xml',
        'wizard/employee_retirement_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
