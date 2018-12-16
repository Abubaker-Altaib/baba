# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'HR Extra Reports',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'HR Extra Reports',
    'description': """

    """,
    
    'depends': [
        'report_webkit',
        'hr_custom',
        'hr_payroll_custom',
        'hr_subsidy',
        'hr_additional_allowance',
        'account_voucher',
        'decimal_precision',

    ],

    'data': [
        
        'report/hr_extra_report.xml',
        'wizard/hr_payroll_expenses.xml',        
  
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
