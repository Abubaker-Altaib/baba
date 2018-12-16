# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2012-2013 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Co-operative Account Management Custom',
    'version': '2.0',
    'category': 'Account Co-operative Management',
    'description': """ Module for Account Co-operative management, It gives the Accounting user the ablitiy to:
			            * determinate  Co-operative Accounts .
			            * determinate  Co-operative Accounts Journals .
           
			
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account'],
    'init_xml': [],
    'data': [
           'security/co-operative_account_management.xml',
           'account.xml',
           


           
    ],
   'test': [],
    
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
