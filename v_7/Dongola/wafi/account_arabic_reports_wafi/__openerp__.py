# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial Arabic Reports Wafi",
    "author" : "NCTR",
    "category": 'Generic Modules/Accounting',
    "description": """
    Modify trial balance & general ledger according to government requirements 
    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    "depends" : ["account_custom_wafi","account_arabic_reports","account_balance_reporting"],
    'data': [
        'report_unit_view.xml',],
    "test" : [],
  
       "demo_xml" : [ ],
        'installable': True,
        'active': False,


}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
