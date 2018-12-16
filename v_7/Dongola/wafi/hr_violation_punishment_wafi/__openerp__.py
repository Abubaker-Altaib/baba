# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Violation & Punishment Management",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "description": "Violation & Punishment Management for wafi",
    "depends": [
        'hr_violation_punishment','hr_wafi'
    ],
    "data" : [
        'hr_violation_punishment_view.xml',
        'hr_employee_violation_workflow.xml',
        'hr_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
