# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Account NTC",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding Features:
    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [
        'security/account_groups.xml',
        'view/payment_voucher.xml',
        'view/account.xml',
        'wizard/operator_view.xml',
        'view/account_report.xml',
        'view/account_budget_operation_view.xml',
        #'view/account_balance_reporting_template_view.xml',
        'wizard/account_exchange_print_wizard_view.xml',
        'wizard/checks_report_view.xml',
        #'wizard/bank_reconsile.xml',
        #'wizard/owner_equity_wizard.xml',

        #'wizard/account_close_period.xml',
        'wizard/account_assistant_report_wizard.xml',
        'wizard/account_report_budget_wizard.xml',
        'wizard/account_report_budget_wizard.xml',
        'wizard/account_report_prepare.xml',
        'wizard/account_pl_close_wizard.xml',
        'wizard/account_fiscalyear_close_wizard.xml',
        #'wizard/account_report_profit_loss_view.xml',
        #'wizard/account_report_balance_sheet_view_ntc.xml',
        #'workflow/invoice_workflow.xml',
        #'workflow/voucher_workflow.xml',
        ],
    "depends" : [
                "account_budget_wafi",
                "account_custom_wafi",
                "account_voucher_custom",
                "account_bank_statement",
                "account_check_writing_custom",
                "account_check_writing_wafi",
        ],
    'test': [],
    'installable': True,
    'active': False,
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
