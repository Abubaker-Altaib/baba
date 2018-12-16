# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial WAFI",
    "author" : "NCTR",
    "category": "Generic Modules/Accounting",
    "description": """
     Modifying fiscal year workflow according to government requirements 
     Displaying account ceiling in statement
    """,
    "version" : "wafi-1.0",
    "website": "http://www.nctr.sd",
    "init_xml": [],
    "depends" : ['account_custom','account_voucher_confirmation','account_bank_statement'],
    "demo" :["demo/account_minimal.xml"],
    "update_xml": [
        'security/account_wafi_security.xml',
        'wizard/account_open_extension_period_wizard_view.xml',
        'account_bank_statement_view.xml',
        'account_view.xml',
        'account_invoice_view.xml',
        'account_invoice_workflow.xml',
        'partner_view.xml',
        
    ],
    'test': [
        'test/account_custom.yml',
        'test/account_move.yml',
        'test/account_move_wizard.yml',
        'test/account_cash_exeed.yml',
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
