# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
        "name" : "Account balance reporting engine",
        "version" : "wafi-1.0",
        "author" : "NCTR",
        "website" : "http://www.nstr.sd",
        "category" : "Enterprise Specific Modules",
        "description": """
            1. Financial Reports
        
            """,
        "depends" : [
                'account_balance_reporting'
        ],
        "data" : [
		        "data/templete_report.xml"       
        ],
        "test": ['test/account_balance_reporting.yml'],
        "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
