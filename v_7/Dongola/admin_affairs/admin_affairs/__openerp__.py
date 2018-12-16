# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Admin Affair",
    "version": '2.0',
    "category": 'Generic Modules/Administrative Affairs',
    "description": """

Admin Affair
============
Admin affair provides integrated controlling and managing for admin affairs operations.

Managing all admin affair operations including:
--------------------------------------

* Configure admin affair accounting, payment roof and service types.
* Manage enrich.

""",
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['fleet','hr_custom','account_voucher','base_custom'],
    "data" : [
	    'security/security.xml',
        'security/ir.model.access.csv',
        "view/admin_affairs_view.xml",
        "view/admin_affairs_payment_roof.xml",
        "view/fleet_management_custom_view.xml",
        "view/enrich_report_view.xml",
        "view/enrich_view.xml",
        "sequence/enrich_sequence.xml",
        "wizard/enrich_report.xml",
        "wizard/solidarity_request_report.xml",
        'view/mail_template.xml'
    ],
    "installable" : True,
}


