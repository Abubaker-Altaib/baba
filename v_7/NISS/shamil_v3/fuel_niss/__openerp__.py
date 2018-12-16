# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##########################################################################

{
    "name" : "Fuel Stock Management Custom",
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
    "depends" : ['fuel_management','stock_negative','stock_oc'],
    "data" : [
        "security/fuel_groups.xml",
	'security/ir.model.access.csv',
        "view/stock_view.xml",
        "wizard/fuel_stock_report.xml",
        'wizard/fuel_movements_wizard_view.xml',
	#'wizard/maintenance_stock_report.xml',
	'wizard/fuel_location_content.xml',
	'report/fuel_report.xml',
    'wizard/fuel_exchange_status_view.xml',
        'view/fuel_exchange_status_archive_view.xml',
        'wizard/fuel_exchange_status_report.xml'
    ],
    "installable" : True,
}

