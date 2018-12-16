# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Media",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Media Section',
    "description": """Media module is for Monitoring press and Requests for media coverage.""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','admin_affairs','hr'],
    'demo': ['media_demo.xml'],
    "data" : [
        "admin_affairs_account_view.xml",
        "media_view.xml",
        "media_service_view.xml",
	"media_report_view.xml",
	"wizard/media_service_wizard.xml",
        "wizard/monitoring_press_wizard.xml",
	"mointor_press_sequence.xml",
	"monitoring_press_workflow.xml",
        "media_service_workflow.xml",
        "security/mp_groups.xml",
        
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
