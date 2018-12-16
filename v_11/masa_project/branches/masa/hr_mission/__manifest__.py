# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'HR Mission',
    'version': '1.0',
    'category': 'HR',
    'description': 
    """
	Manage Employee Mission
    """,
    'author': "NCTR",
    'website': 'http://www.nctr.sd',
    'depends': ['hr_custom','hr_payroll_custom','account_expense'],
    'data': [
	'security/ir.model.access.csv',
        'security/hr_mission_security.xml',
        'views/hr_mission_view.xml',
        'views/hr_mission_category_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
