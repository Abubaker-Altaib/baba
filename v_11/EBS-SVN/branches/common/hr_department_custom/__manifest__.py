# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name': "Department Custom",
    'summary': "Add analytic account to department",
    'author': "NCTR",
    'website': "http://www.nctr.sd",
    'category': 'HR',
    'version': 'EBS',
    'depends': ['base', 'hr', 'analytic'],

    'data': [
        'views/hr_department.xml',
		'views/res_users.xml',
    ],

    'demo': [
        
    ],
}
