# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Custom Inventory Management",
    "version" : "1.1",
    "author" : "NCTR",
    "description" : """ Custom Inventory Management
    	 -Prevent changes in Inventory after Confirm
    """,
    "website" : "http://www.nctr.sd",
    'depends' : ["stock",],
    'category' : "Warehouse Management",
    'demo' : [
    	#"demo/stock_inventory_demo.yml"
    ],
    'data' : [
                  "product_view.xml",        
    ],
    'test': [
    	"test/stock_inventory.yml"
    ],
    'installable': True,
    'auto_install': False,


}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
