# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'GDS project',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'linking payments with finger print',
    'description': """

    """,
    'website': 'https://www.nctr.sd',
    'depends': [
        'hr','resource' , 'web'
        #'web_module',
    ],
    'data': [
    'wizard/finger_print_wizard_view.xml',
    'views/gds_view.xml',
    'views/payment_workflow.xml',
    'views/employee_payment_action_view.xml',
    'wizard/payment_receive_view.xml',
    ],
    'js': [
        'static/src/js/finger_print.js',
        #'static/src/js/Nitgen.js',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
