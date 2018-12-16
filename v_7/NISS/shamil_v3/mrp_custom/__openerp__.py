# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
        "name" : "MRP: Production customization",
        "version" : "wafi-1.0",
        "author" : "NCTR",
        "website" : "http://www.nstr.sd",
        "category" : "Enterprise Specific Modules",
        "description": """
            1. Translation
        
            """,
        "depends" : [
                'mrp','production_costs'
        ],
        "data" : [
            'mrp_view.xml',

            'report/production_cost_view.xml',
            #'report/production_order.xml',
            'report/sale_report_view.xml',


        ],
        "test": [],
        "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
