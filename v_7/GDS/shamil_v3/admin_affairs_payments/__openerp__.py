# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Admin Affairs Payment",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs',
    "description": """Manage Admin Affairs Payment Procedures.....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','admin_affairs',],
    "data" : [
    "enrich_view.xml",
    "enrich_report_view.xml",
    "workflow/enrich_workflow.xml",
    "workflow/enrich_lines_workflow.xml",
    "sequence/enrich_sequence.xml",
    "wizard/enrich_report.xml",

    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
