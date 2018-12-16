# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Base Custom',
    'version' : '1.1',
    'author' : 'NCTR',
    'website': 'http://www.nctr.sd',
    'description' : """Add the following features: 1-Amount To Text Arabic """,
    'depends' : ['base','web','mail'],
    'data': [
        'security/base_custom_security.xml',
        'security/ir.model.access.csv',
        'data/res_currency_demo.xml',
        'views/ir_attachment_view.xml',
        'views/res_company.xml',
        'views/res_currency_view.xml',

    ],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
