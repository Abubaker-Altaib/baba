# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Recruitment Custom",
    "version": "1.1",
    "category": "Generic Modules/HR",
    "description": """
HR Recruitment
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["hr_custom","hr_recruitment", 'account_fiscalyear'],
    "data": [
        "security/hr_recruitment_custom_security.xml",
        "security/ir.model.access.csv",
        "views/hr_recruitment_custom.xml",
        "wizard/wizard.xml",
    ],
    'demo': [
        #'data/hr_recruitment_demo.xml',
    ],
    "installable": True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
