# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Stock Report",
    "version": "7.0",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
     Module for  Inventory Control reporting
     """,
    "category": "Warehouse Management",
    "website": "http://www.nctr.sd",
    "depends": ["stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
		"wizard/location_content.xml",
		"wizard/products_zero.xml",
        #'wizard/incoming_products.xml',	
        'wizard/exchange_position_statistic.xml',
	    "wizard/stock_location_product_view.xml",
        "report/stock_arabic_report.xml",
        "report/stock_arabic_report.xml",	
        #"wizard/delv_by_depts_view.xml",	
        "stock_report.xml",
	],
    "test": [
    	"test/stock_report.yml"
    ],

    "installable": True,
    "auto_install": False,
    "active": False,
 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
