# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Account Voucher Custom For EBS",
    "version": "1.0 EBS",
    "category": "Accounting & Finance",
    "description": """
            Customization for EBS.""",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_voucher_custom"],
    "data": [
        #"views/account_voucher_workflow.xml",
        "views/account_voucher_view.xml",
        "views/account_payment.xml"
    ],
    "test": [
        #"test/account_voucher.yml"
    ],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
