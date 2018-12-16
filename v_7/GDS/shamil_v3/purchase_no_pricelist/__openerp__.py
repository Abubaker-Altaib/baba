# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#  This module is responsible for customizing purchase order and order lines 

{
    'name': 'Custom Purchase Management',
    'version': '1.2',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """This module is purchase customization it contains the following features:
         * Editing the purchase order workflow
         * Depends on currency of company not currency from pricelist
         * No pricelist at all   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['base','purchase','hr'],
    'init_xml': [],
    'data': [
           'purchase_view.xml',
           'purchase_workflow.xml',
           'purchase_report.xml',
    ],
    'test': [
            #'test/print_purchase_order_report.yml',
            #'test/purchase_order_canceling.yml',
            #'test/invoice_creation_from_picking.yml',
            #'test/delete_purchase_order.yml',
            #'test/sign_order.yml',
    ],
    'demo': [
         #  'demo/partner_demo.xml',
           ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

