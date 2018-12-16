# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Admin Affairs",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs',
    "description": """Manage Admin Affairs Procedures.....""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['stock','account_financial_ratification','base','fleet','hr','product'],
    "data" : [
    "admin_affairs_view.xml",
    "fleet_manager_custom_view.xml",
    "fleet_manager_custom_workflow.xml",
    "admin_affairs_sequence.xml",
    "product_view.xml",
    "admin_affairs_payment_roof.xml",
    "admin_voucher.xml",

    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
