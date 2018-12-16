# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Employee Directory Custom NTC",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "depends": ['hr_grant_rights','hr_loan','hr_training_wafi','hr_violation_punishment_wafi',
        'hr_evaluation_custom', 'hr_holidays_buy', 'hr_payroll_wafi', 'hr_wafi' , 'purchase_ntc','report_webkit' , 'admin_affairs', 
        'hr_additional_allowance','report_xls'],
    "data" : [
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/hr_employee_view.xml',
		'views/hr_substitution_workflow.xml',
		'views/hr_delegation_workflow.xml',
		'views/hr_wafi_process_workflow.xml',
		'views/hr_workflow.xml',
		'views/holidays_data.xml',
		'views/hr_data.xml',
		'views/holidays_template.xml',
		'views/hr_template.xml',
		'views/hr_payroll_view.xml',
		'data/data_lang.xml',
		'views/hr_mission_view_ntc.xml',
		#'data/currency_data.xml',
		'views/hr_training.xml',
		'views/hr_holidays_workflow.xml',
		'views/hr_training_workflow.xml',
		'data/allow_account_data.xml',
		'views/hr_violation_punishment.xml',		
		'wizard/cat_report_wiz.xml',
		'wizard/qual_report_wiz.xml',
		'wizard/bonus_listing.xml',
   		'views/hr_holidays.xml',
    	'wizard/payroll_report_bank.xml',
        'wizard/training.xml',
    	'wizard/payroll_budget_wiz.xml',
	    'wizard/training_reports_wiz.xml',
	    'wizard/allow_deduct_exception.xml',
		'views/training_custom_view.xml',
		'wizard/departments_wizard.xml',
		'views/training_template.xml',
		'wizard/departments_wizard.xml',
	    	'wizard/hr_employee_report.xml'
		],
    "demo": [],
    "test": [],
    "installable": True, 
}
