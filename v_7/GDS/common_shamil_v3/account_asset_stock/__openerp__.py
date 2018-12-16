# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "stock asset",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding the following Features:
    1. link stock to asset.

    """,
    "version" : "shamil-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    "depends" : ["stock_multi_company","account_asset_custody"],
    'data' : [
        "stock_view.xml",
        "asset.xml",
             ],
    'test': [],
    'installable': True,
    'active': False,

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
