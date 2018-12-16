# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Stock Quality",
    "version" : "1.1",
    "author" : "NCTR",
    "description" : """ Stock Quality
    """,
    "website" : "http://www.nctr.sd",
    "depends" : ["stock","purchase"],
    "category" : "Warehouse Management",
    "demo" : [
    	#"demo/stock_quality_demo.yml"
    ],
    "data" : [
        "security/stock_quality_security.xml",
        "stock_view.xml",
        "stock_quality_sequence.xml",
        "stock_report.xml",
    ],
    "test": [
    	"test/stock_quality.yml"
    ],
    "installable": True,
    "auto_install": False,


}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
