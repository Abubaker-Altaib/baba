# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Hijri Reports",
    "version": "Maknoun",
    "category": "Generic Modules/Accounting",
    "description": """
    Add Hijri date to budget reports 
    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget_custom","budget_custom_report"],
    "data": [
        "report/budget_certification_template_hijri.xml",
        "report/print_budget_template_hijri.xml",
        "report/budget_comparison_template_hijri.xml",
        "wizard/budget_comparison_view_hijri.xml",
        "report/budget_main_template_hijri.xml",
        "wizard/budget_main_view.xml",

        

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
