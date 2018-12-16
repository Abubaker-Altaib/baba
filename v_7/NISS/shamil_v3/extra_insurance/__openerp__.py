# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Extra Insurance",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Extra Insurance',
    "description": """Extra Insurance module is for Sea Insurance and Stock Insurance and any Extra insurance.""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','admin_affairs','hr','purchase'],
    "data" : [
	"wizard/stock_insurance_fill.xml",
        "sea_insurance.xml",
	"stock_insurance.xml",
	"bankers_insurance.xml",
        "insurance_report.xml",
	"insurance_seq.xml",
	"wizard/bankers_insurance_wiz_view.xml",
	"wizard/total_insurance.xml",
	"insurance_workflow.xml",
        "admin_affairs_account_view.xml"
    ],
    "installable" : True,
}
