# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#  This module is responsible for customizing purchase order and order lines 

{
    'name': 'Cooperative Stock Inventory Management Custom',
    'version': '1.2',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """This module is stock inventory customization """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['stock_inventory','cooperative_stock'],
    'init_xml': [],
    'data': ['wizard/summrize_stock_inventory_wizard.xml',
             'inventory_reports.xml',
             'security/stock_cooperative_inventory.xml',
             ],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

