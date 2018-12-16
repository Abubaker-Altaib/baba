# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Training Human Resources",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "description": "Human Resources management for training module",
    "depends": [
        'hr_payroll_custom','hr_custom'
    ],
    "data" : [
        'security/training_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'hr_config.xml',
        'hr_training_view.xml',
        'hr_training_process.xml',
        'hr_training_workflow.xml',
        'company_view.xml',
        'report/hr_training_report.xml',
        'wizard/department_course.xml',
        'wizard/hr_approve_course_wizard.xml',
        'wizard/stat_part.xml',
        'wizard/no_training.xml',
		'wizard/test_free2.xml',
        'wizard/shamil_training_report.xml',
		'wizard/course_form.xml',
		'wizard/evo_training.xml',
		'wizard/suggest_vs_approved.xml',

    ],
    'test': [],
}
