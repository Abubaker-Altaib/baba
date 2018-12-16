# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Stock Exchange Management",
    "version": "1.1",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
    stock exchange module is for generating a exchange order for exchange of goods 
    """,
    "website": "http://www.nctr.sd",
    "depends": ["stock_account_internal",],
    "category" : "Warehouse Management",
    "init_xml" : [],
    #"demo"     : [
    #    "demo/stock_exchange_demo.yml"
    #],
    "data" : [
        "security/stock_exchange_security.xml",
        "security/ir.model.access.csv",
        "company_view.xml",
        "stock_exchange_workflow.xml",
        "stock_exchange_sequence.xml",
        "wizard/exchange_fill_package.xml",
        "stock_exchange_view.xml",
        "stock_view.xml",
        "stock_exchange_report.xml",
        "wizard/exchange_partial_picking_view.xml",
        "wizard/stock_exchange_report.xml",
        "package_view.xml",
    ],
    #"test" : [
        #"test/exchange.yml",
        #"test/exchange_store.yml",
        #        "test/exchange_report.yml"
    #],
    "installable": True,
    'application': True,
    "auto_install": False,

    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
