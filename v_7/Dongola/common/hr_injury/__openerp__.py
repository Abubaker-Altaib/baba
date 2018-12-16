# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Injury',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employee Injury',
    'description': """
Human Resources Management
==========================
    """,
   'depends': ['hr_custom','hr_payroll_custom'],
    'data': [
        'data/sequence.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/hr_injury_wizard_view.xml',
        'wizard/hr_injury_wizard_report_view.xml',
        'hr_injury_view.xml',
        'hr_injury_workflow.xml',
        'company_view.xml',
        'report/hr_injury_report_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
