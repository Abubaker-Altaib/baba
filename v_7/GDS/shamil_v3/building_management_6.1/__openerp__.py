# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

{
    "name" : "building management module",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/building management',
    "description": """This module manage all building operation like insurance and maintenance""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','hr','admin_affairs','purchase_custom'],
    "data" : [
    "view/building_manager_view.xml",
    "view/building_maintenance.xml",
    "view/building_accident.xml",
    "view/building_management_report.xml",
    "view/admin_affairs_account_view.xml",
    "view/building_insurance_view.xml",
    "sequence/building_maintenance_sequence.xml",
    "sequence/building_accident_seq.xml",
    "sequence/building_insurance_sequence.xml",
    "security/building_security.xml",
    "wizard/building_fill_insurance_view.xml",
    "wizard/building_accident.xml",
    "wizard/building_maintenance_wizard.xml",
    "wizard/building_insurance_wizard.xml",
    "workflow/building_maintenance_workflow.xml",
    "workflow/building_insurance_workflow.xml",
    "workflow/accident_workflow.xml",

    ],
    "installable" : True,
}
