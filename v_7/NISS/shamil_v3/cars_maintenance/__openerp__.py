# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Car Maintenance module",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Services Section',
    "description": """Cars Maintenance module manage all cars maintenance requests and operations .....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base_custom','admin_affairs','hr_custom','account_voucher'],
    "data" : [
	    "car_maintenance_request_view.xml",
	    "car_maintenance_report.xml",
	    "car_maintenance_category_view.xml",
	    "admin_affairs_account_view.xml",
	    "car_maintenance_archive_view.xml",
	    "security/car_maintenace.xml",
	    "car_maintenance_sequence.xml",
	    "workflow/car_maintenance_request_workflow.xml",
	    "wizard/car_maintenance.xml",
	    #"wizard/cars_maintenance_type.xml",
	    "wizard/car_maintenace_allowances_view.xml",
	    "product_view.xml"
    ],
    "installable" : True,
}
