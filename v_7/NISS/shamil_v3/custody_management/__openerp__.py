# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Custody Management',
    'icon': "/custody_management/static/img/icon.png",
    'version': '2.0',
    'category': 'Account Asset Managemet',
    'description': """Module for Request to pact
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account','account_asset',],
    'init_xml': [],
    'demo_xml' : ['demo_data.xml'],
    'data': ['asset_pact_view.xml',
             'release_order_workflow.xml',
             'asset_pact_workflow.xml',
             'release_order_view.xml',
             'pact_order_sequence.xml',
             'custody_reports.xml',
             'release_order_sequence.xml',
             'custody.xml' ,
             'wizard/partial_release_wizrd.xml',
             'wizard/custody_report_wizard.xml',
             'security/custody_management_security.xml'



],
    
    'installable': True,
    'application':True ,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
