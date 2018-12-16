# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employee Appraisals Custom',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Periodical Evaluations, Appraisals, Surveys',
    'description': """
Periodical Employees evaluation and appraisals
==============================================


""",

    
    'depends': ['hr_evaluation'],
    'data': [
        'security/hr_evaluation_security.xml',
        'security/ir.model.access.csv',
        'hr_evaluation_view.xml',
        
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
