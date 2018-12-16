# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Account Financial Reports Hijri",
    "version": "Maknoun",
    "category": "Generic Modules/Accounting",
    "description": """

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["account_finance_reporting","hijri_datepicker","account_bank_statement_reconciliation",
"account_voucher_custom","account_check_printing_custom"],
    "data": [
        "report/report_payment_voucher_template_hijri.xml",
        "report/report_journal_custom.xml",
        "report/account_bank_statement_reconcilation_report_template.xml",
        "report/bank_transfer_report.xml",
        "report/report_account_statement_hijri.xml",
        "report/report_journal_hijri.xml",
        "report/report_financial_hijri.xml",
        "wizard/account_statement_view_hijri.xml",
        "wizard/account_report_analytic_statement_hijri.xml",
        "wizard/account_report_print_journal_view_hijri.xml",
        "wizard/account_financial_report_view_hijri.xml",

    ],
    "installable": True,
    "active": False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
