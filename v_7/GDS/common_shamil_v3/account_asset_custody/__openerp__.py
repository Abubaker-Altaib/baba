# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Asset Custody Customization",
    "version": "7.0",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
     Module for  Inventory Control reporting
     """,
    "category": "Account Asset",
    "website": "http://www.nctr.sd",
    "depends": ["account_asset_custom","hr_payroll_custom","stock_exchange"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
	
		'asset_custody.xml',
		'asset_custody_sequence.xml',
        'asset_custody_workflow.xml',
	    "wizard/asset_location_product_view.xml",
	    "wizard/asset_custody_view .xml",
	    "wizard/detail_custody_view.xml",
	    "wizard/personal_custody_view.xml",
	    "wizard/management_custody_view.xml",
        #'report/asset_barcode_print.rml',
	    
	],
   
    "installable": True,
    "auto_install": False,
    "active": False,
 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
