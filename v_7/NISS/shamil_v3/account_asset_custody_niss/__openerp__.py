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
    "depends": ["stock_multi_company", "stock_niss","stock_account_internal","account_asset_stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
        "security/custody_security.xml",
        "security/ir.model.access.csv",
        "account_asset_custody_report.xml",
        "asset_custody_workflow.xml",
        "asset_custody.xml",
        "user.xml",
        "stock_view.xml",
	    
	],
   
    "installable": True,
    "auto_install": False,
    "active": False,
 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
