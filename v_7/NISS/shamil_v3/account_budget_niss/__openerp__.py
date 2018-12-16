# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Account Budget niss",
    "version": "7.0",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
     Module for  Account Budget niss
     """,
    "category": "Account",
    "website": "http://www.nctr.sd",
    "depends": ["account_budget_custom"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
        "account_budget_niss_view.xml",
        "sequence/account_budget_niss_sequence.xml",
        "account_report_niss.xml",
	],
   
    "installable": True,
    "auto_install": False,
    "active": False,
 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
