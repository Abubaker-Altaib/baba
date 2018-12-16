# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Purchase Wafi",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Purchase Management",
    "description": "Customize purchase requisition & purchase order according to government's process.",
    "depends": [
        'purchase_requisition',
        'account_custom_wafi',
        'hr_custom',
        "base_custom",
        ],
    "data" : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/purchase_data.xml',
        'view/purchase_view.xml',
        'view/purchase_workflow.xml',
        'view/purchase_requisition_workflow.xml',
        'view/purchase_requisition_order_report_view.xml',
        'wizard/purchase_requisition_group_view.xml',
        'report/purchase_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
