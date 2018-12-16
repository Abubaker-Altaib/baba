# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2013 NCTR (<http://www.nctr.sd>).
#
##########################################################################


{
    "name" : "Cars operation Modules",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Car operation Section',
    "description": """Cars operation module manages all Car operations like license and insurance""",
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','admin_affairs','hr','account_voucher'],
    "data" : [
    "view/car_operation_view.xml",
    "view/car_operation_report.xml",
    "view/admin_affairs_account_view.xml",
    "sequence/car_operation_sequence.xml",
    "workflow/car_operation_workflow.xml",
    "security/car_operation.xml",
    "wizard/car_operation_wizard.xml",
    "wizard/car_operation_report_wiz.xml",

    
    ],
    "installable" : True,
}
