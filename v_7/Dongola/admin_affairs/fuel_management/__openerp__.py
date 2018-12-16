# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##########################################################################

{
    "name" : "Fuel Management",
    "version": '2.0',
    "category": 'Generic Modules/Administrative Affairs',
    "description": """

Fuel management module
======================
Fuel management provides integrated controlling and managing for fuel.

Managing all fuel operation including:
--------------------------------------

* Configure fuel products.
* Compute the portion of fixed and extra fuel for vehicles.
* Compute the spent amount on fuel portions.

""",
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['stock','admin_affairs','account_voucher','hr_custom','hr_mission'],
    "data" : [
        "security/fuel_groups.xml",
	    'security/ir.model.access.csv',
        "view/product_view.xml",
        "view/fuel_details_view.xml",
        "view/fleet_log_fuel_view.xml",
	    "wizard/fuel_qty_line_wizard_view.xml",
        "view/fuel_plan_view.xml",
        
        "view/fuel_request_report.xml",
        "view/fuel_plan_report.xml",
        "view/fuel_request_notification_report.xml",
        "wizard/compare_fuel_wizard_view.xml",
        "wizard/fuel_plan_report_wizard_view.xml",
        "wizard/fuel_request_report_wizard_view.xml",
        "wizard/fuel_monthly_plan_wizard_view.xml",
        
        "sequence/fuel_sequence.xml",

        "wizard/service_cars_fuel_report.xml"
    ],
    "installable" : True,
}

