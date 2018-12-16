# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2013 NCTR (<http://www.nctr.sd>).
#
##########################################################################


{
    "name" : "HR Personal Tax percentage",
    "category": 'Generic Modules/HR',
    "description": """Allow to manage payroll personal tax percentage that the tax will be taken from""",
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','hr_payroll_custom'],
    "data" : [
    "view/tax_percentage_view.xml",
    ],
    "installable" : True,
}
