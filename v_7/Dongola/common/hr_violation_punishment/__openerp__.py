# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Violation and Punishment',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employee Violation and Punishment',
    'description': """
Employee Violation and Punishment
==========================


    """,

    'images' : ['images/violations.png'],
    'depends': ['hr_payroll_custom'],
    'data': [
       'security/ir.model.access.csv',
       'hr_violation_punishment_view.xml',
       'report/hr_report.xml',
       'hr_violations_punishment_workflow.xml',
       'wizard/emp_violations_punishments.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
