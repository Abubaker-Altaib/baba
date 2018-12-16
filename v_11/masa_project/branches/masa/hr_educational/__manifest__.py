# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'HR Educational ',
    'version': '1.0',
    'category': 'HR',
    'description': 
    """
	Manage Employee Educational
    """,
    'author': "NCTR",
    'website': 'http://www.nctr.sd',
    'depends': ['hr_custom','hr_recruitment_custom','hr_payroll_custom'],
    'data': [
         'views/hr_educational_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
