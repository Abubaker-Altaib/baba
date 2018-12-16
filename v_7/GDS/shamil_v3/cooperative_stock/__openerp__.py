# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2012-2013 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Cooperative Stock Management Custom',
    'version': '2.0',
    'category': 'Cooperative Stock Management',
    'description': """ Module for Cooperative Stock management, It gives the stock user the ablitiy to:
			* determinate the co-operative products categories.
            * Reports about co-operative incoming shippments .
            * Reports about co-operative Delivery Orders .
			
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['stock','stock_multi_company','stock_exchange','account', 'cooperative_sale'],
    'init_xml': [],
    'data': [
           'security/co-operative_stock _management.xml',
           'stock.xml',
           'stock_co_operative_reports.xml',
           'stock_co_operative_reports_wizard.xml' ,
           'exchange_order_workflow.xml' ,
           'wizard/location_content_co_oprative.xml',
           'wizard/co_operative_incoming_shippment.xml',
           'wizard/co_operative_delivery_orders.xml',



           
    ],
   'test': [],
    
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
