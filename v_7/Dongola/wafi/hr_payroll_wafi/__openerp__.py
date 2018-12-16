# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Payroll Wafi",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "description": "Payroll for wafi",
    "depends": [
        'hr_payroll_custom',
    ],
    "data" : [
       # 'data/salary_scale.xml',
        'data/degree_category.xml',
        'hr_payroll_view.xml',
        'hr_substitution_workflow.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
