# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Stock NTC",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding Features:
    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [
        'workflow/stock_workflow.xml',
        'wizard/stock_partial_picking_view.xml',
        'wizard/stock_transfer_picking_view.xml',
        'wizard/exchange_position_statistic.xml',
        'view/stock_ntc_view.xml',
        'view/stock_reports.xml',
        
        ],
    "depends" : ["stock","purchase_wafi","stock_custom","stock_negative","base_custom",'stock_report'],
    'test': [],
    'installable': True,
    'active': False,
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
