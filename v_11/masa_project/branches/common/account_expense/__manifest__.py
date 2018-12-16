# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Expense',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
Add all information on voucher.

    """,
    'website': 'https://www.odoo.com/page/employees',
    'depends': ['account_voucher_custom','hr_department_custom'],
    'data': [


        'views/account_expense_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
