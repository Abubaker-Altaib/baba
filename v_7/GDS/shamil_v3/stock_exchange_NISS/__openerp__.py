# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Stock Exchange customization for NISS",
    "version": "1.1",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
    Customize Stock Exchange
    """,
    "website": "http://www.nctr.sd",
    "depends": ["stock_exchange",],
    "category" : "Warehouse Management",
    "init_xml" : [],
   
    "data" : [
        "product_view.xml",  
        "stock_view.xml",
        "stock_exchange_report.xml",
        "user.xml",  
    ],
    
    "installable": True,
    'application': False,
    "auto_install": False,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
