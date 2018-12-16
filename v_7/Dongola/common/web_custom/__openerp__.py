# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Web Custom",
    "author" : "NCTR",
    "category": 'Web',
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    "depends" : ["web"],
     "js":[
        "static/src/js/view_form_custom.js",
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    "installable": True,
    
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
