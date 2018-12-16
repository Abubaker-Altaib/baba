#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Services modules",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Services Section',
    "description": """Services Department manages all services .....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','admin_affairs','hr','account_voucher'],
    'demo': ['services_demo_data.xml'],
    "data" : [
    "hospitality_service_view.xml",
    "hospitality_service_report.xml",
    "rented_cars_view.xml",
    "rented_cars_request.xml",
    "environment_and_safety_archive.xml",
    "environment_and_safety.xml",
    "admin_affairs_account_view.xml",
    #"account_analytic.xml",
    "outsite_contract1_view.xml",
    "service_request_view.xml",

    "service_sequences.xml",
    
    
    "hospitality_service_workflow.xml",
    "rented_cars_request_workflow.xml",
    "rented_cars_workflow.xml",
    "enviroment_Safety_workflow.xml",
    "environment_and_safety_workflow.xml",
    "halls_lock_workflow.xml",
    "contract_fees_workflow.xml",
    "service_request_workflow.xml",

    
    "wizard/hospitality_allowances_view.xml",
    "wizard/rented_cars_allowances_view.xml",
    "wizard/rented_cars.xml",
    "wizard/hospitality_services_wiz.xml",
    "wizard/gov_rent_car.xml",
    #"wizard/enviroment_and_safety_allow_wiz.xml",
    "wizard/enviroment_and_safety_wizard.xml",
    #"wizard/environment_and_safety_allownes_report_wiz.xml",
    "wizard/renew_rented_cars.xml",
    "wizard/outsite_contract_allowances.xml",
    "wizard/outsite_contract_atten_over.xml",
    
    ],
    "installable" : True,
}
