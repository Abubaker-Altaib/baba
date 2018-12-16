# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Employees Committes',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Operations Committes Details',
    'depends': ['hr_custom_military', 'hr_mission', 'hr_payroll_custom_niss'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'views/committe_view.xml',
        'wizards/commites_wizard.xml',
        'views/modified_views.xml',
        'views/res_config_view.xml',
        'wizards/hr_bonus_candidates_wizard.xml',
        'wizards/hr_promotion_candidates_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
