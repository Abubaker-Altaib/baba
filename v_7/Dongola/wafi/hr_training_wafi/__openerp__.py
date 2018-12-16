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
        'hr_training'
    ],
    "data" : [
        'hr_training_view.xml',
        'hr_training_process.xml',
        'hr_training_workflow.xml',
        'hr_training_plan_workflow.xml',
        'wizard/hr_approve_course_wizard.xml'
    ],
    'test': [],
}
