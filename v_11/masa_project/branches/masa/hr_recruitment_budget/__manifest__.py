# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Hr Recruitment Budget',
    'version': '1.0',
    'category': 'HR',
    'description': 
    """
	Manage Recruitment Budget
    """,
    'author': "NCTR",
    'website': 'http://www.nctr.sd',
    'depends': ['hr_custom','hr_recruitment_custom'],
    'data': [
         "views/hr_recruitment_budget_view.xml",
 	     "views/hr_job_views.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
