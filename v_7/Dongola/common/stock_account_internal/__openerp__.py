# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Stock Accounting  Internal",
    "version": "1.1",
    "author": "NCTR",
    "complexity": "easy",
    "description": """Generate accounting moves when doing internal moves""",
    "category" : "Warehouse Management",
    "website": "http://www.nctr.sd",
    "depends": ["stock","hr"],
    "demo" : [
        #"demo/account_stock_internal_demo.yml"
    ],
    "data" : [
      "stock_view.xml" ,
    ],
    "test":[
        "test/account_stock_internal.yml"
     ],

    "installable": True,
    "auto_install": False,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
