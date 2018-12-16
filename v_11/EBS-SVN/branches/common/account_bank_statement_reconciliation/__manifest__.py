# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Account Bank Statement Reconciliation",
    "author" : "NCTR",
    "category": "base",
    "description": """
     Adding the following Features:
    1. Partner & Tax Customization.
    """,
    "website": "http://www.nctr.sd",
    "depends" : ['account_custom','account_cancel'],
    "data": [
        'views/account_bank_statement_reconciliation.xml',
        'report/account_bank_statement_reconcilation_report_template.xml',
        'report/account_bank_statement_reconcilation_report.xml',
	'wizard/generate_stmt_journal_entries.xml',
        
    ],
    "installable": True,
}
