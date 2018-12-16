# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Employee Additional Allowances",
    "version": "1.1",
    "category": "Human Resources",
    "description": """ Module allowing ...
    """,
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ["hr_payroll_custom", "hr_holidays_custom"],
    "data": [
        "security/ir.model.access.csv",
        "hr_additional_allowance_workflow.xml",
        "hr_additional_allowance.xml",
    ],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
