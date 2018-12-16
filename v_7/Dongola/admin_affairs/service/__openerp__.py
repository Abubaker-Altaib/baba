#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
	"name" : "Service Management",
	"version" : '2.0',
	"category": 'Generic Modules/Administrative Affairs',
	"description": """

service
=======
service provides integrated controlling and managing for services.

Managing all services operation including:
--------------------------------------

* Configure admin affairs services.
* Manage all contracts operations for different types of services.
* Compute and transfer contracts costs.

""",
	"author" : 'NCTR',
	"website": "http://www.nctr.sd",
	"depends" : ['admin_affairs','account_voucher_custom','stock','base_custom','purchase_wafi'],
	"data" : [
		'security/security.xml',
		'security/ir.model.access.csv',
		'wizard/vehicle_maintenance_purchase.xml',
        'view/building_view.xml',
        'view/contract_custom_view.xml',
		'view/services_view.xml',
		'view/fleet_log_contract_view.xml',
		'view/license_insurance.xml',
		'view/contracts_view.xml',
		'wizard/vehicle_rent_renew_waz.xml',
		'wizard/rented_cars.xml',
		'wizard/gov_rent_car.xml',
		'wizard/location_wizard_view.xml',
		'wizard/contract_transfer.xml',
		'wizard/vehicle_rent_extend_waz.xml',
		'wizard/service_wizard_view.xml',
		'view/service_request.xml',
		'report/cars_maint_noti_report.xml',
		#'data/data.xml',
		'sequence/sequence.xml',
		'view/dashboard.xml',
		'wizard/hall_calendar_wizard.xml',
	]
}
