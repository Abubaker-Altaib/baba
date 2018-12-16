# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Indirect Treasury Feeding",
    "author" : "NCTR",
    "category": "Generic Modules/Accounting",
    "description": """
    This module divide feeding treasury operation to two steps :
    1. From request to pay: journal entry will create between pay journal account (cr) & partner account (dr)
    2. Receiving:  journal entry will create between partner account (cr) & treasury account (dr)
    """,
    "version" : "wafi-1.0",
    "website": "http://www.nctr.sd",
    "depends" : ['account_voucher_wafi'],
    "demo" :[],
    "data": [
        'account_custom.xml',
        'account_voucher_workflow.xml'
    ],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
