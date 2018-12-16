# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Mission Fuel Request",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Fuel Request',
    "description": """Fuel request module is to request fuel for mission from missions form.""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','hr_mission','fuel_management'],
    "data" : [
        "fuel_request_view.xml",
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
