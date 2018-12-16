# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Holidays Custom",
    "version": "Maknoun",
    "category": "Generic Modules/HR",
    "description": """
HR Holidays Custom
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["hr_holidays","hr_payroll",'hr'],
    "data": [
        "views/hr_holidays_custom.xml",
        #"views/hr_programming_holidays.xml",
    ],
    "installable": True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
