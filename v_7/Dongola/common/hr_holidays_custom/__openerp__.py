# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Leave Management Custom',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Human Resources',
    'website': 'http://www.nctr.sd',
    'summary': 'Employees Leave Management',
    'description': """
Manage leaves and allocation requests
=====================================

This application controls the holiday schedule of your company. It allows employees to request holidays. Then, managers can review requests for holidays and approve or reject them. This way you can control the overall holiday planning for the company or department.

You can configure several kinds of leaves (sickness, holidays, paid days, ...) and allocate leaves to an employee or department quickly using allocation requests. An employee can also make a request for more days off by making a new Allocation. It will increase the total of available days for that leave type (if the request is accepted).

You can keep track of leaves in different ways by following reports: 

* Leaves Summary
* Leaves by Department
* Leaves Analysis

A synchronization with an internal agenda (Meetings of the CRM module) is also possible in order to automatically create a meeting when a holiday request is accepted by setting up a type of meeting in Leave Type.
""",
    'depends': ['hr_holidays','hr_payroll_custom'],
    'data': [
        #'security/ir_rule.xml',
        #'security/ir.model.access.csv',
        'hr_employee_view.xml',
        'hr_holidays_view.xml',
        'absence_view.xml',
        'hr_holidays_workflow.xml',
        'company_view.xml',
        'wizard/holi_analysis.xml',
        'wizard/holi_free.xml',
        'wizard/holi_info.xml',
        'wizard/submiting.xml',
        'report/holidays_reports_view.xml',
        'scheduler.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
