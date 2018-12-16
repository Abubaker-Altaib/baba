# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": 'Purchase Clearance Customization',
    "version": '1.0',
    "category": 'Purchase Management',
    "description": """Module for Purchase Clearance Customization and extra requirments
		   """,
    "author": 'NCTR',
    "website": 'http://www.nctr.sd',
    "depends": ['purchase_clearance'],
    "init_xml": [],

    "data": [
   # 'clearance_view.xml',
	'workflow/clearance_workflow.xml',
 ],

    "installable": True,
   

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
