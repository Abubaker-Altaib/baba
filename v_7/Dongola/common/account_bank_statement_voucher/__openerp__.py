# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Bank Statement Voucher",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """ 
Create Voucher from Bank Statement
==================================
This module allow accountant to create expense/revenues voucher from any bank statement line which present a moves appear in bank not in journal.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_bank_statement","account_check_writing_custom"],
    "data": [
        "account_bank_statement_view.xml",
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
