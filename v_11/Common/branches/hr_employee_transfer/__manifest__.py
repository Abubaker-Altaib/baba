# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
#######################################################################
{
    'name': 'Employee Transfer',
    'version': 'Maknoun',
    'summary': 'Employee transfer between depatrment',
    'category': 'Generic Modules/Human Resources',
    'author': "NCTR",
    'website': "http://www.nctr.sd",
    'depends': ['hr_custom'
                ],
    'data': [
        'views/employee_transfer.xml',
        'data/sequence.xml',
    ],
    "installable": True,
    "active": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
