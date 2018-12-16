# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Financial Ratification  niss",
    "version": "shamil-1.0",
    "category": "Generic Modules/Finance",
    "description": """ Module allowing all depatments employee Request a Financial Ratification,
    and make ratification going through Ratification Company's Procedures. """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_financial_ratification",],
    "init_xml": [],
    "test": [

     ],
    "data": [
        "security/account_ratification_workflow_security.xml",
        "financial_ratification.xml",
        "financial_ratification_workflow.xml",
        "report/account_report.xml",

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
