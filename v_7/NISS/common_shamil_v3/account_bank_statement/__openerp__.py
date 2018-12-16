# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Bank Statement",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """ 
Configurable Statement Formula
==============================

This module make bank statement methodology configurable for company by adding the calculation formula & statement condition within company's configuration.

Beside prevent creating any journal entry from bank statement or cash register.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account"],
    "data": [
        "account_account_view.xml",
        "account_bank_statement_view.xml",
        "report/account_report.xml",
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
