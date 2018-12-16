# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name': 'Stock Custom',
    'version': '1.0',
    'category': 'Stock',
    'description': """
Stock Custom Module
==================================================


* Add changes in Inventory 



    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'images' : [],
    'depends': ['stock','account_custom','hr','purchase_ntc'],
    'data': [
        'security/security.xml',
        'res_config_view.xml',
        'stock_view.xml',
        'stock_workflow.xml',
        'wizard/stock_partial_picking_view.xml',
        'wizard/stock_partial_move_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
