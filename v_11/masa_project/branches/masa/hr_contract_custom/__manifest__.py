# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'HR Contract Custom',
    'version': '1.1',
    'category': 'Generic Modules/HR',
    'description': """
    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['hr_custom','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
