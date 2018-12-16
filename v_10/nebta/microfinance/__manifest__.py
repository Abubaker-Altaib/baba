# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Financing Management',
    'version': 'Nabta v1',
    'author': 'NCTR',
    'description': """
Financing management.
==========================================

This Module add feature:
\nFinancing Order
\nPortfolio  Management
\nReport.

    """,
    'website': 'http://www.nctr.sd',
    'category': 'Accounting & Finance',
    'sequence': 32,
    'images': ['static/description/Nabta.png'],
    "depends" : ["base","account_check_printing_custom"],
    'demo': [],
    'test': [],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'sequence/finance_order_seq.xml',
        'demo_data/portfolio_formula.xml',
        'views/finance_management.xml',
        'views/micro_finance.xml',
        'views/micro_finance_config.xml',
        'views/micro_finance_portfolios_view.xml',
        'views/microfinance_visit.xml',
        'views/report_view.xml',
        'views/app_icons_custom.xml',
        'wizard/wizards_view.xml',
        'wizard/portfolio_State.xml',
        'reports/reports_template.xml',
        'reports/contract_report_template.xml',
        'wizard/reports_render.xml',
        'wizard/arab_fund_wizard.xml',
        'wizard/customer_state_wizard_view.xml',
        'wizard/customer_state_template.xml',
        'wizard/contract_wiz_view.xml',
        #'wizard/arab_fund_report_template.xml',
        #'workflows/micro_finance_individual_order_wkf.xml',
    ],

    'qweb': [
        'static/src/xml/custom_thread.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
