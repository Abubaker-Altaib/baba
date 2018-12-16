# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'HR Subsidy',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'HR Subsidy',
    'description': """
Human Resources Management
==========================


    """,

    
   'depends': ['hr','hr_custom','hr_payroll_custom'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'hr_subsidy_report_view.xml',
        'hr_subsidy_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
