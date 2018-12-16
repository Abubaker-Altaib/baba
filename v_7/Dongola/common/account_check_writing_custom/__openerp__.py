# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name" : "Check Writing Custom",
    "version": "wafi-1.0",
    "category": "Generic Modules/Accounting",
    "description": """ Module allowing printing bank letters & cheques for any bank payment (if payment bank allow check writing),
     If payment has already been paid with check it allows:
        1. Reprint the existing check.
        2. Print a new check.
        3. Update Supplier Payment’s Check No.
        4. Print a new check
    """,
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ["account_custom","account_voucher_custom","audittrail" ],
    "data": [
        "security/account_checkwriting_security.xml",
        "security/ir.model.access.csv",
        "wizard/account_check_print_wizard_view.xml",
        "wizard/account_bank_letter_view.xml",
        "wizard/account_bank_transference_letter_view.xml",
        "wizard/account_check_cancel_view.xml",
        "account_view.xml",
        "account_check_cancel_data.xml",
        "account_voucher_view.xml",
    ],
    "demo_xml": [
        "data/check_writing_audit.xml",
        "data/check_sequence.xml",
    ],
    "test": [],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
