# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employees Alternative',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Operations Alternative Details',
    'depends': ['hr', 'hr_payroll_custom', 'hr_custom_military'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'sequance/sequance_definition.xml',
        'views/alternate_setting_view.xml',
        'views/alternate_process_view.xml',
        'wizards/alternate_report_wizard.xml',
        'reports/alternate_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
