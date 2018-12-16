# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Leave buying Management',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Leave  buying Management',
    'description': """
Manage leaves buying & buying amount calculate
=====================================

This application controls the holiday buying of your company. It allows manager to request buying employee's holidays.
You can configure the calculation amount from leave configuration. 


""",
    
    'depends': ['hr_holidays_custom','hr_payroll_custom'],
    'data': [
        'hr_holidays_buy_report.xml',
        'hr_holidays_buy_view.xml',
        'hr_holidays_buy_workflow.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
