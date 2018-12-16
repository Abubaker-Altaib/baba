# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Directory Custom Niss',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Jobs, Departments, Employees Details',
    'description': """
Human Resources Management
==========================


    """,

    
    'depends': ['hr_additional_allowance', 'hr_injury','hr_violation_punishment' ,'hr_holidays_custom','hr_mission','hr_custom','hr_payroll_custom_niss','hr_holidays_custom','hr_mission','hr_custom'],
    'data': [
        'payroll_view.xml' ,
        'hr_view.xml',
        'hr_process_view.xml',
        'gift_view.xml',
        'hr_process_workflow.xml',
        'sequance_definition.xml',
        'luggage_destination.xml',
        'wizard/job_degree_wizard.xml',
        'wizard/luggage_transfer.xml',
        'wizard/hr_employee_process_wizard.xml',
        'wizard/hr_employee_promotion_wizard.xml' ,
        'wizard/emp_record_wizard_report.xml' ,
        'hr_holidays_view.xml',
	    'hr_commision_view.xml',
        'data/sequance.xml',
        'res_config_view.xml',
        'res_company_view.xml',
        'hr_extra_view.xml',
	    'hr_mission_view.xml' ,
        'report/hr_report.xml',
        'data/sequance.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': ['static/src/css/style.css' ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
