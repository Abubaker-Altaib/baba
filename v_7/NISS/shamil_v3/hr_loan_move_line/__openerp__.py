# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2013 NCTR (<http://www.nctr.sd>).
#
##########################################################################


{
    "name" : "HR Loan Payment Move Line",
    "category": 'Generic Modules/HR',
    "description": """Allow to create move line for each employee""",
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['hr_loan','hr_payroll_custom'],
    "data" : [
    "hr_loan_view.xml",
    ],
    "installable" : True,
}
