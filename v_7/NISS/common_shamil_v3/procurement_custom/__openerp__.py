# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    "name" : "Procurements Custom",
    "version" : "1.0",
    "author" : "NCTR",
    "complexity": "easy",
    "website" : "http://www.nctr.sd",
    "category" : "Hidden/Dependency",
    "depends" : ["procurement"],
    "description": """

    """,
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        "wizard/product_order_point.xml",
        "procurement_view.xml",
    ],
    "test": [
        "test/procurement_custom.yml"
    ],
    "installable": True,
    "auto_install": False,
    "active": False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
