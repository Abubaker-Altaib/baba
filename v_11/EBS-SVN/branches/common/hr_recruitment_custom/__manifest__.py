# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "HR Recruitment Custom",
    "version": "Maknoun",
    "category": "Generic Modules/HR",
    "description": """
HR Recruitment
================================

    """,
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "depends": ["hr","hr_recruitment", 'account_fiscalyear', 'hr_payroll_custom'],
    "data": [
        "views/hr_job_views.xml",
        "views/hr_recruitment_custom.xml",
        "wizard/wizard.xml",
        "wizard/job_cancel_wiz_view.xml",
        "wizard/job_merge_wiz_view.xml",
        "wizard/job_tranfer_wiz_view.xml",
    ],
    "installable": True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
