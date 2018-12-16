# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Purchase NTC",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Purchase Management",
    "depends": ['purchase_wafi'],
    "data" : [
	'data/purchase_ntc_data.xml',
	'security/security.xml',
	'security/ir.model.access.csv',
	'view/purchase_view.xml',
        'view/purchase_requisition_workflow.xml',
        'view/stock_workflow.xml',
	'view/purchase_order_workflow.xml'
    ],
}
