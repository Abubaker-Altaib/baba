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

    
    'depends': ['hr_additional_allowance', 'hr_injury','hr_violation_punishment' ,'hr_holidays_custom','hr_holidays_buy','hr_mission','hr_custom','hr_payroll_custom_niss', 'hr_loan'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'workflow/hr_delegation_workflow.xml',
        'report/hr_report.xml',
        'hr_view.xml',
        'hr_process_view.xml',
        'gift_view.xml',
        'hr_process_workflow.xml',
        'hr_delegation_workflow.xml',
        'sequance_definition.xml',
        'luggage_destination.xml',
        'wizard/job_degree_wizard.xml',
        'wizard/luggage_transfer.xml',
        'wizard/hr_employee_process_wizard.xml',
        'wizard/hr_employee_seniority_wizard.xml',
	    'wizard/hr_employee_promotion_wizard.xml' ,
        'wizard/dept_duration_report_wizard.xml',
        'wizard/residence_report_wizard.xml',
        'hr_holidays_view.xml',
	    'hr_commision_view.xml',
        'data/sequance.xml',
        'res_config_view.xml',
        'res_company_view.xml',
        'hr_extra_view.xml',
        'hr_employee_seniority.xml',
	    'hr_mission_view.xml' ,
        'employee_more_menu_view.xml',
        'payroll_view.xml' ,
        'reports.xml',
        'wizard/promotion_group_by_job.xml',
        'wizard/service_state_wizard.xml',
        'wizard/loan_candidates_wizard.xml',
        'wizard/degree_company_report_view.xml',
        'hr_transfer_wishes.xml',
        'wizard/training_report_view.xml',
        'wizard/escape_status_report_view.xml',
        'wizard/dep_status_report_view.xml',
        'wizard/absence_report_view.xml',
        'wizard/salary_suspend_report_view.xml',
        'wizard/tribe_report_view.xml',
        'wizard/batch_report_view.xml',
        'wizard/transfer_wish_view.xml',
        'status_report_config.xml',
        'wizard/hr_promotion_candidates_wizard.xml',
        'wizard/long_service_report_view.xml',
        'wizard/emp_delegation_report_wizard.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': ['static/src/css/style.css' ], 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
