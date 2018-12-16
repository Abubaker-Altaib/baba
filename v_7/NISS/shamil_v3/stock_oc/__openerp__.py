# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

{
    "name" : "Stock management OC",
    "version": '1.1',
    "category": 'Stock management/OC Specification',
    "description": """Stock management OC Specification .....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['stock_niss','stock_exchange_NISS','purchase_customization','stock_exchange_purchase_requestion','account_asset_custody_niss'],
    "data" : [
     "security/stock_exchange_security.xml",
     "view/stock_view.xml",
     "view/stock_exchange_workflow.xml",
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
