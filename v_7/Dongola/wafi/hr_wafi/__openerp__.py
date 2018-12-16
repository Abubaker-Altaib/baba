# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Human Resources Wafi",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "description": "Human Resources management for wafi",
    "depends": [
        'hr_custom',
    ],
    "data" : [
        'hr_view.xml',
        'hr_workflow.xml',
        #'hr_wafi_process_sequence.xml',
        'hr_wafi_process_workflow.xml',
        'hr_job_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
