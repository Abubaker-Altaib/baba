# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Account Invoice Confirmation",
    "version" : "shamil-1.0",
    "author" : "NCTR",
    "category": "Generic Modules/Accounting",
    "description": """This module adding Confirmation field to invoice, 
    and use this confirmation when creating invoice moves.
    """,
    "init_xml": [],
    "depends" : ["account","account_budget_confirmation"],
    "update_xml": [
        "account_invoice_view.xml",        
    ],
   "test": [
        "test/account_invoice_confirmation.yml",
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
