# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Custom Inventory Management",
    "version" : "7.0",
    "author" : "NCTR",
    "complexity": "easy",
    "description" : """
        Module can manage multi-warehouses, multi and stock locations when use multi-companies. 
    """,
    "website" : "http://www.nctr.sd",
    "depends" : ["stock",],
    "category" : "Warehouse Management",
    "demo" : [
       # "demo/stock_multi_company_demo.yml"
    ],
    "data" : [
		"security/stock_multi_company_security.xml",
        "stock_view.xml",
    ],
    "test": [
   # "test/stock_multi_company.yml"
        ],
    "installable": True,
    "auto_install": False,
    "active": False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
