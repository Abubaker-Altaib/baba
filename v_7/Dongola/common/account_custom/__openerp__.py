# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Accounting and Financial",
    "author" : "NCTR",
    "category": "Generic Modules/Accounting",
    "description": """
     Adding the following Features:
    1. Accounting Rules & Groups.
    2. Modify value_amount field in account.payment.term.line model to accept more than 2 decimal accuracy.
    3. Modify compute methond in res.currency model to get the rate from res.currency.rate according to date.
    4. Add sequence_id to period & create the sequence when period create.
    5. Account parent must be in the same company.
    6. Closing Fiscalyear wizard work with multi-companies.
    7. Header for reporst 
    8. Make Account Treasury Graph-DashBoard invisible
    9. close account fiscalyear and create entries in new fiscalyear 
    """,
    "version" : "wafi-1.0",
    "website": "http://www.nctr.sd",
    "depends" : ['account','audittrail','base_custom'],
    "demo" :[],
    "data": [
        'security/account_groups.xml',
        'security/account_rule.xml',
        'security/ir.model.access.csv',
        'wizard/account_fiscalyear_close_view.xml',
        'wizard/account_pl_close.xml', 
        'account_custom.xml',
        'wizard/account_curency_close_view.xml',
        'wizard/account_move_reverse.xml', 
        'wizard/account_tree.xml',
        'wizard/account_chart_view.xml',
        'account_data.xml',
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
