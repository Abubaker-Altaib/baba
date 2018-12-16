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
    "category": 'Generic Modules/Administrative Affairs/Booking Service',
    "description": """Booking custom module is to connect missions and training with booking service for booking tickets.""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','hr_mission','hr_training','public_relation'],
    "data" : [
        "booking_custom_view.xml",
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
