# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Custom",
    "version": "1.1",
    "category": "Generic Modules/HR",
    "description": """
HR Custom
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends":["hr","base_custom"],
    "data": [
        "security/hr_custom_security.xml",
        "security/ir.model.access.csv",
        "wizard/job_cancel_wiz_view.xml",
        "wizard/job_merge_wiz_view.xml",
        "wizard/job_tranfer_wiz_view.xml",
        "views/hr_views.xml",
        "views/hr_qualification_experience_views.xml",
        "views/employee_transfer.xml",
        "views/employee_medical_insurance.xml",
    ],
    "installable": True,
    "active": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
