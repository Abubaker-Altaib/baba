# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
        "name" : "Account balance reporting engine wafi",
        "version" : "wafi-1.0",
        "author" : "NCTR",
        "website" : "http://www.nstr.sd",
        "category" : "Enterprise Specific Modules",
        "description": """
        This module modify balance calculation in balance reporting model by ignoring previous periods.
            """,
        "depends" : [
            'account_custom_wafi', 'account_arabic_reports', 'account_balance_reporting'
        ],
        "data" : [ 
            'report/account_balance_reporting_reports.xml',
            'data/template_report.xml',
        ],
        "test": [],
        "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
