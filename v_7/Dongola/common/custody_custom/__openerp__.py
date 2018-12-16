# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Custody Management Custom',
    'version': '2.0',
    'category': 'Warehouse',
    'summary' : 'Custodies and Custodies Operations',
    'description': """ The Purpose of this module is managing custodies operations.
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['stock_custom'  , 'asset_custody_management','base_custom' , 'stock_ntc'],
    'init_xml': [],
    'data': [ 'views/stock_view.xml',
              'views/custody_release_order_workflow.xml',
              'views/custody_release_order.xml',
             



],
    'demo_xml' : [],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
