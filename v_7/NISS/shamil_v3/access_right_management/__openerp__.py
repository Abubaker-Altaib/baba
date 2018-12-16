# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Access Rights Managment',
    'version': '1.1',
    'author': 'NCTR',
    #'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Provide Access Rights For user by IT User',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_groups_view.xml',
	    'views/log_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

