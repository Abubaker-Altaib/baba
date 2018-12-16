# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Payroll Holidays",
    "version": "Maknoun",
    "category": "Generic Modules/HR",
    "description": """
HR Holidays Custom
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["hr_holidays_custom","hr_payroll_custom",'hr'],
    "data": [
        "views/hr_payroll_holidays.xml",
       
    ],
    "installable": True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
