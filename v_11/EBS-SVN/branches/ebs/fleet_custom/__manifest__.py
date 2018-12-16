# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    'name' : 'Fleet Custom',
    'version' : '1.1',
    'sequence': 165,
    'category': 'Human Resources',
    'author': 'NCTR',
    'website' : 'http://www.nctr.sd',
    'summary' : 'Vehicle, leasing, insurances, costs',
    'description' : """
Vehicle, leasing, insurances, cost
==================================
With this module, Odoo helps you managing all your vehicles, the
contracts associated to those vehicle as well as services, fuel log
entries, costs and many other features necessary to the management 
of your fleet of vehicle(s)

Main Features
-------------
* Add vehicles to your fleet
* Manage contracts for vehicles
* Reminder when a contract reach its expiration date
* Add services, fuel log entry, odometer values for all vehicles
* Show all costs associated to a vehicle or to a type of service
* Analysis graph for costs
""",
    'depends': ['fleet',],
    'data': [
        'views/fleet_vehicle_views.xml',
        'views/fleet_vehicle_cost_views.xml',
    ],

    'demo': [],

    'installable': True,
    'application': True,
    'atuo_install':False,
}
