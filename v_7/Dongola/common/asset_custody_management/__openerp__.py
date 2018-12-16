# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Custody Management',
    'version': '2.0',
    'category': 'Asset and Warehouse Management',
    'summary' : 'Custodies and Custodies Operations',
    'description': """The Purpose of this module is managing custodies operations.
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['product' , 'stock', 'hr' ,'account_asset' ,'account_asset_custom' , 'asset_ntc_custom'],
    'init_xml': [],
    'demo_xml' : ['demo_data.xml'],
    'data': [
             'security/custody_management_security.xml',
             'asset_pact_view.xml',
             'custody.xml' ,
             'release_order_workflow.xml',
             'asset_pact_workflow.xml',
             'release_order_view.xml',
             'sequence/pact_order_sequence.xml',
             'custody_reports.xml',
             'stock_view.xml',
             'sequence/release_order_sequence.xml',
             'data/custody_scheduler.xml',
             'wizard/partial_release_wizrd.xml',
             'wizard/custody_report_wizard.xml',
             'wizard/add_items_operation_wizard.xml',
             



],

    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
