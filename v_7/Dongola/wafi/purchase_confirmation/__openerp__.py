# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Purchase Confirmation Wafi",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Purchase Management",
    "description": "Link purchase requisition with budget confirmation",
    "depends": [
        'purchase_wafi',
        'account_budget_confirmation'],
    "data" : [
        'purchase_view.xml',
        'purchase_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
