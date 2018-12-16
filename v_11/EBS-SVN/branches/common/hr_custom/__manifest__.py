# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Custom",
    "version": "Maknoun",
    "category": "Generic Modules/HR",
    "description": """
HR Custom
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["hr","base_custom","hr_department_custom"],
    "data": [
        "views/company_view.xml",
        "security/hr_custom_security.xml",
        "views/hr_views.xml",
        "views/employee_family.xml",
        "views/hr_qualification_experience_views.xml",
        "views/employee_transfer.xml",
    ],
    "installable": True,
    "active": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
