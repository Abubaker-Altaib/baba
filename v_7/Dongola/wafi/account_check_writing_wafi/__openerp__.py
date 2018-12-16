# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Check Writing",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """ 
    Module modify printing check & bank letter according to wafi voucher workflow
    and modify canceling payment as governments requirements  
    """,
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ["account_check_writing_custom","account_voucher_wafi"],
    "data": [
        "account_voucher_view.xml",
        "wizard/account_check_cancel_view.xml",
    ],
    "test": [],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
