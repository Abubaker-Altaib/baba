# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
        "name" : "Account balance reporting engine",
        "version" : "wafi-1.0",
        "author" : "NCTR",
        "website" : "http://www.nstr.sd",
        "category" : "Enterprise Specific Modules",
        "description": """
The module allows the user to create account balance reports and templates,
comparing the values of 'accounting concepts' between two fiscal years
or a set of fiscal periods.

Accounting concepts values can be calculated as the sum of some account balances,
the sum of its children, other account concepts or constant values.

Generated reports are stored as objects on the server,
so you can check them anytime later or edit them
(to add notes for example) before printing.

The module lets the user add new templates of the reports concepts,
and associate them a specific "XML reports" (OpenERP RML files for example)
with the design used when printing.
So it is very easy to add predefined country-specific official reports.

The user interface has been designed to be as much user-friendly as it can be.

Note: It has been designed to meet Spanish/Spain localization needs,
but it might be used as a generic accounting report engine.
            """,
        "depends" : [
                'account', 'account_arabic_reports'
        ],
        "data" : [
                'security/ir.model.access.csv',
                'account_balance_reporting_template_view.xml',
                'account_balance_reporting_view.xml',
                'account_balance_reporting_reports.xml',
		        #"data/templete_report.xml"       
        ],
        "test": ['test/account_balance_reporting.yml'],
        "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
