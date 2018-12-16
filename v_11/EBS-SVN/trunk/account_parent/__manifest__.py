# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Parent Account",
    'summary': "Adds Parent account",
    'description': """
This module will be very useful for those who are still using v7/v8 because of the no parent account in the latest versions
        * Adds parent account in account
        * Adds new type 'view' in account type
        * Adds credit, debit and balance in account
        * Shows chart of account based on the date and target moves we have selected
    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'category': 'Accounting &amp; Finance',
    'version': '1.2.1',
    'depends': ['account','account_custom'],
    'data': [
        'security/account_parent_security.xml',
        'views/account_view.xml',
        'data/account_type_data.xml',
    ],
}
