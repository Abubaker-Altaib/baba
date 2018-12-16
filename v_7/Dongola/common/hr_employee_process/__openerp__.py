# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Process',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Jobs, Departments, Employees Details',
    'description': """
Human Resources Management
==========================
Employee Process : Departments movements , Change Job , promotion or yearly bonuse
    """,

    
    'depends': ['base','hr_payroll_custom'],
    'data': [
        'security/hr_emp_process_security.xml' , 
        'wizard/hr_bonus_candidates_wizard.xml',
        'wizard/hr_promotion_candidates_wizard.xml' ,
        'wizard/hr_employee_process_wizard.xml' ,
        'hr_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
