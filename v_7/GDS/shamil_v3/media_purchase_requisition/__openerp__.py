# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Media purchase requistion",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Media Section',
    "description": """Media purchase requistion module is for create purchase requisition from media service order.""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['media','purchase_custom'],
    "data" : [
      'media_service_view.xml'  
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
