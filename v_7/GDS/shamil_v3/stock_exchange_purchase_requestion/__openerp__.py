# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Stock Exchange Purchase requestion",
    "version": "1.1",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
    stock exchange Purchase requestion module is for generating a purchase requestion form the exchange order 
    if the items is not avaliable in the stock by adding new wizard in exchange order view 
    """,
    "website": "http://www.nctr.sd",
    "depends": ["stock_exchange","purchase_custom","purchase_foreign"],
    "category" : "Warehouse Management",
    "init_xml" : [],
    "data" : [

        "wizard/create_purchase_requestion_view.xml",
        "stock_exchange_view.xml",
        "internal_requistion_view.xml",
        "internal_requestion_workflow.xml",
        "stock_exchange_workflow.xml",
        
    ],
    
    "installable": True,
    'application': True,
    "auto_install": False,

    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
