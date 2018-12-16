# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Attendance NTC",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding Features:
    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [
        'security/security.xml',
        'view/attendance_view.xml',
        'data/attendance_scheduler.xml',
        'wizard/attendance_fetch.xml'
        ],
    "depends" : [
                "hr_attendance_custom",
                'report_webkit'
        ],
    'test': [],
    'installable': True,
    'active': False,
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
