# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Public Relation",
    "version": '1.1',
    "category": 'Generic Modules/Administrative Affairs/Public Relation Section',
    "description": """Public Relations Department manages the affairs of foreigners, hotel bookings and also is responsible for dealings with travel agencies with respect to extracting tickets and payment of financial claim""",
    
    "author" : "NCTR",
    "website": "http://www.nctr.sd",
    "depends" : ['base','hr_custom','hr_mission','account_voucher','admin_affairs','services'],
    "data" : [
        "public_relation_view_foreigner.xml",
	    "occasion services.xml",
	    "public_relation_report.xml",
	    "ticket_booking.xml",
	    "hotel_service_view.xml",
	    "public_relation_sequences.xml",
	#"security/pr_f_groups.xml",
        "foreigners_request_workflow.xml",
        "ticket_booking_workflow.xml",
	    "occasion_service_workflow.xml",
        "hotel_service_workflow.xml",
        "wizard/foreigners_procedures_wiz.xml",
	    "wizard/foreigners_procedures_wiz_speciftic_time.xml",
	    "wizard/foreigners_details_wiz.xml",
        "wizard/hotel_service.xml",
	    "wizard/ticket_booking.xml",
        "admin_affairs_account_view.xml",
    ],
    "installable" : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
