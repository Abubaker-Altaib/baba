# -*- encoding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name': '''Purchase Requisition with Budget Confirmation''',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """  Purchase with Budget confirmation this module gives the ability to check
               the budget for the ordered products by sending the selcted quote's total price to budget confirmation
               if there is avalible budget or not for this order""",
    'author': 'NCTR',
    'website': 'http://www.nctr.com',
    'depends': [
        'purchase_custom','hr','account_invoice_confirmation'
    ],
    'data': [
        'internal_requisition_with_budget_workflow.xml',
        'internal_requisition_with_budget_view.xml',
    ],

    'test': [
        'test/internal_requestion_with_budget.yml',
        'test/create_invoice_and_picking_by_budget_id.yml'
        ],

        
    'demo': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
