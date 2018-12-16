# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Stock Archive",
    "version": "7.0",
    "author": "NCTR",
    "complexity": "easy",
    "description": """
     Module for archiving stock Picking 
     """,
    "category": "stock",
    "website": "http://www.nctr.sd",
    "depends": ["stock","sale"],
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
        "stock_archive.xml",
        "sequence/stock_archive.xml",
	],
   
    "installable": True,
    "auto_install": False,
    "active": False,
 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
