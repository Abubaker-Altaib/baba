# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "HR Payroll Deposit",
    "version" : "shamil-1.0",
    "author" : "NCTR",
    "category": 'Generic Modules/HR/Payroll',

    'init_xml': [],
    "depends" : ['hr_payroll_custom','hr_custom'],
    'data': [
        'hr_payroll_deposit.xml',
        'res_company_view.xml',
        'hr_payroll_deposit_sequence.xml',
        'wizard/hr_payroll_deposit_wizard.xml',
        'hr_payroll_deposit_workflow.xml',
        
    ],
   'test': [],
   
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
