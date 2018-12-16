# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': "Sudan - GFS Accounting",
    'version': "0.1",
    'category': 'Localization/Account Charts',
    'description': """This is the base module to manage the accounting chart for Sudan GFS in Odoo.""",
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        'account_template.xml',
        'account_chart.xml',
        'l10n_su_wizard.xml',
    ],
    'demo_xml': [ ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
