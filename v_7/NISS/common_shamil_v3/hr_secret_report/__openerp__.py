# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employees Secret Report',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'depends': ['hr_custom_military'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        #'views/alternate_setting_view.xml',
        'views/hr_secret_report.xml',
        'report/secret_report_reports.xml',
        'wizard/brief_secret_report_wizard.xml',
    ],
    'css': ['static/src/css/style.css' ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
