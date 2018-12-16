# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
###############################################################################


{
    'name': 'Attendances Of Employees',
    'version': '1.1',
    'category': 'Generic Modules/Human Resources',
    'description': """
    This module customize the employee's attendances module Add attendances record 
    to each Employee.
       """,
    'website': "http://www.nctr.sd",
    'author': 'NCTR',
    'depends': ['hr_payroll','hr_attendance','resource', 'hr_custom'],
    'data': [
        'views/hr_attendance_view.xml',
        'views/hr_attendance_device_view.xml',
        'wizard/attendace_record_wizard_view.xml',
        'data/attendance_record_scheduler.xml',
    ],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
