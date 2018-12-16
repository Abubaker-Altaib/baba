# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Employee Custom Niss",
    "version": '1.0',
    "category": 'Human Resources',
    "description": """
	This module provides:
		* controlling on who can see employee's personal data 

	""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ['hr_payroll_custom'],
    "data": [
	'security/groups.xml',
	'view/hr_employee.xml',
    ],
    "installable": True,
}


