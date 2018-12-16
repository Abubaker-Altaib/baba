# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial Custom",
    "author" : "NCTR",
    "category": "Accounting",
    "description": """
     Adding the following Features:
    1. Partner & Tax Customization.
    """,
    "website": "http://www.nctr.sd",
    "depends" : ['account','account_invoicing'],
    "data": [
        'views/account_custom.xml',
        'security/account_custom_security.xml',
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
