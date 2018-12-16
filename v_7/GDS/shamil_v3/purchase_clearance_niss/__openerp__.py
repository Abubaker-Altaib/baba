# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": 'Purchase Clearance Customization',
    "version": '1.0',
    "category": 'Purchase Management',
    "description": """Module for Purchase Clearance Customization and extra requirments
		   """,
    "author": 'NCTR',
    "website": 'http://www.nctr.sd',
    "depends": ['purchase_clearance','board'],
    "init_xml": [],

    "data": [
       'clearance_view.xml',
       'clearance_report_view.xml',
       'wizard/clearance_report_niss.xml',
       'wizard/dependence_letter_report.xml',
       'wizard/im_certificate_report.xml',
       'wizard/port_fee_letter_report.xml',
       'wizard/customs_fee_letter_report.xml',
       'wizard/added_value_letter_report.xml',
       'wizard/clearance_report_niss_all.xml',
       'wizard/group_voucher_partner_view.xml',
       'wizard/clearance_finance_report.xml',
       'wizard/general_clearance_report.xml',
 ],

    "installable": True,
   

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
