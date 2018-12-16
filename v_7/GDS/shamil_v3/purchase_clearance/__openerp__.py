# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Purchase Clearance",
    "version": '1.1',
    "category": 'Generic Modules/Purchase Clearance',
    "description": """Purchase clearance module is for generating a clearance for purchase of goods from a supplier.
    A supplier invoice is created for the particular order placed""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','purchase','stock','account_voucher','purchase_foreign','purchase_report'],
    "data" : [
	    "security/clearance_groups.xml",
        "clearance_view.xml",
        "clearance_config.xml",
        "purchase_view.xml",
	    "clearance_report_view.xml",
        "company_view.xml",
	    "sequence/clear_sequence.xml",
	    "workflow/clear_workflow.xml",
        "wizard/create_clearace_from_po.xml",
	    #"wizard/clearance_report_All.xml",
        
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
