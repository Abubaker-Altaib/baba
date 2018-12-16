# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Nebta HR Management',
    'version': 'Nabta v1',
    'author': 'NCTR',
    'description': """
Humane resource management.
==========================================

This Module add feature:
\nCustom Report.

    """,
    'website': 'http://www.nctr.sd',
    'category': 'hr',
    'sequence': 32,
    'images': ['static/description/Nabta.png'],
    "depends" : ["hr","hr_payroll", "base","microfinance"],
    'demo': [],
    'test': [],
    'data': [
        'views/hr_menu.xml',
        'views/custom_hr_view.xml',
        'reports/hr_report_template.xml',
        'wizard/hr_wizards_view.xml',
        'wizard/reports_render.xml',
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'sequence/finance_order_seq.xml',
           ],
    'auto_install': False,
    'installable': True,
    'application': True,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
