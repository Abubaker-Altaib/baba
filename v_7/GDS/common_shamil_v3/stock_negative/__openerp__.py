# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Prevent negative stock quantities",
    "version" : "7.0",
    "author" : "NCTR",
    "complexity": "easy",
    "description" : """ Prevent negative stock quantities
    """,
    "website" : "http://www.nctr.sd",
    "depends" : ["stock",],
    "category" : "Warehouse Management",
    "demo" : [
    	#"demo/stock_negative_demo.yml"
    ],
    "data" : [
		"wizard/stock_partial_move_view.xml",
    	"wizard/stock_partial_picking_view.xml",        
    ],
    "test": [
        "test/stock_negative_test.yml"
    ],
    "installable": True,
    "auto_install": False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
