# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Missions',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employee Missions',
    'description': """
Employee Missions
==========================


    """,
    'depends': ['hr_payroll_custom'],
    'data': [
        'security/hr_mission_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'hr_mission_view.xml',
        'company_view.xml',
        'hr_mission_workflow.xml',
        'report/hr_report.xml',
        #'wizard/mission_state.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
