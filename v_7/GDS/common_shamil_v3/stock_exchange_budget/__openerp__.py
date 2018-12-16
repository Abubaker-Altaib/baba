# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Stock Exchange budget Management",
    "version": "1.1",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
    stock exchange budget module is for make a exchange order passes through budget confirmation
    """,
    "website": "http://www.nctr.sd",
    "depends": ["stock_exchange","account_budget_confirmation"],
    "category" : "Warehouse Management",
    "init_xml" : [],
    "demo"     : [],
    "data" : [
        "stock_exchange_workflow.xml",
        "stock_exchange_view.xml", 
    ],  
    "installable": True,
    'application': False,
    "auto_install": False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
