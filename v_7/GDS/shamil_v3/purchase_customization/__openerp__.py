# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#  This module is responsible for customizing purchase order and order lines 

{
    'name': 'Purchase Customization',
    'version': '1.2',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """This module is customizing the purchase_custom module""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['purchase_custom','purchase_foreign','purchase_multi_suppliers','purchase_report','stock_multi_company'],
    'init_xml': [],
    'data': ['security/purchase_order_group.xml',
             'wizard/create_partial_picking.xml',
             'purchase_view.xml',
			 'internal_requisition_view.xml',
             'internal_requesition_workflow.xml',
             'purchase_customization_reports.xml',
             'user.xml',
             #'res_partner.xml',
             'ir_sequence.xml' ,
             'sequence/internal_requesition_sequence.xml',
             'sequence/quote_sequence.xml',
             #'sequence/purchase_sequence.xml',
             'wizard/incoming_products.xml',
             'wizard/request_financial_ratification.xml',
             'wizard/search_and_inform.xml',
             'wizard/create_partial_picking_report.xml',
             'wizard/intial_request_summation.xml',
             'wizard/purchases_position_statistic.xml',
             'wizard/purchases_suppliers_report.xml',
             #'wizard/purchases_orders_status.xml',
            ],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

