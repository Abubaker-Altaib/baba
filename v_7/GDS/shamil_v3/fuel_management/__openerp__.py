# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

{
    "name" : "fuel management module",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/fuel management',
    "description": """fuel management .....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','media','hr','stock','fleet'],
    "data" : [
     "vehicles_fuel_details_view.xml",
     "wizard/stock_return_picking_view.xml",
     "fuel_request.xml",
     "product_view.xml",
     "fuel_plan_view.xml",
     "fuel_view.xml",
     "fuel_data.xml",
     "admin_affairs_account_view.xml",
     "fuel_request_notification_report.xml",
     "fleet_view.xml",
     "fuel_sequence.xml",
     "security/fuel_groups.xml",
     "fuel_request_workflow.xml",
     "fuel_plan_workflow.xml",
     "fuel_picking_workflow.xml",
     "wizard/fuel_request_report_wizard_view.xml",
     "wizard/fuel_monthly_plan_wizard_view.xml",
     "wizard/cars_mission.xml",
     "wizard/fuel_partial_picking_view.xml",
     #"wizard/fuel_move.xml",
     "wizard/compare_fuel.xml",
     "wizard/fuel_plan_report_wizard_view.xml",
     "wizard/fuel_location_product_view.xml",
     "report/vehicles_fuel_details_report_view.xml",
     "report/fuel_plan_report.xml",

    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
