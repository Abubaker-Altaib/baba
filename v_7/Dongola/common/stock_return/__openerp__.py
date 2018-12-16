# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name': 'Stock Return',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Stock Return',
    'description': """
Stock Return Module
==================================================

* Improve Stock Pick Return add workflow

    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'images' : [],
    'depends': ['stock'],
    'data': [
        'stock_view.xml',
        'stock_workflow.xml',
        'stock_sequence.xml',

    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
