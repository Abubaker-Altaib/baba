# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Budget Management EBS",
    "version": "shamil v4, wafi v2",
    "category": "Generic Modules/Accounting",
    "description": """
Budget Management
================================
This module allows accountants to manage analytic and budgets operations.
    * Entering Fisacal Years & Periods Budget. also provides some budget operations (increasing, transfering,...)
    * Allow printing three types of Budget Reports:

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget_custom","account_parent"],
    "init_xml": [],
    "data": [
        #"data/sequence.xml",
        "security/account_budget_security.xml",
        #"security/ir.model.access.csv",
        'wizard/add_accounts_and_lines_wizard_view.xml',
        "views/account_budget_view.xml",
        "views/account_budget_operation_view.xml",
        "views/account_budget_confirmation_view.xml",
        #"views/account_budget_confirmation_view.xml",
        "data/demo_data_for_report_fromat.xml", 
	    "report/action_print_budget_line.xml",
        "report/template_print_budget_line.xml",
        #"wizard/budget_comparsion_wizard_view.xml",
        #"templates/budget_comparsion_template.xml",
        'wizard/add_accounts_and_lines_wizard_view.xml',
        'wizard/print_budget_lines_wizard_view.xml',
        
    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
