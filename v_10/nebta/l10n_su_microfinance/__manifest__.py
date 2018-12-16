# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sudan - Microfinance',
    'version': 'Nabta v1',
    'author': 'NCTR',
    'category': 'Localization',
    'description': """
This is the base module to manage the Sudan microfinance accounting chart in Odoo.
==============================================================================

Install some generic chart of accounts.
    """,
    
    'website': 'http://www.nctr.sd',
    'depends': [
        'account',
    ],
    'data': [
        'data/l10n_su_microfinance_data.xml',
        'data/account_financial_report_data.xml'
    ],
}
