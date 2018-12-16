# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Account FiscalYears & Periods",
    "author" : "NCTR",
    "category": "Accounting",
    "description": """
     Adding the following Features:
    1.Adding fiscalyears & periodsperiod.
    """,
    "website": "http://www.nctr.sd",
    "depends" : ['account', 'account_voucher'],
    "data": [
        'wizard/account_period_close_view.xml',
        'views/account_fiscalyear.xml',
        'views/account_move.xml',
        'wizard/account_fiscalyear_close_state.xml',
        "security/ir.model.access.csv",
        'wizard/account_pl_close.xml',
        
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
