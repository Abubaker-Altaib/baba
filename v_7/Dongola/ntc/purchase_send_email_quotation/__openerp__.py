# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
{
    "name": "Purchase Send Email Quotation",
    "version": "1.0",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Purchase Management",
    "depends": ['purchase_ntc'],
    "data" : [
    
    'security/security.xml',
    'wizard/purchase_send_email_quotation_wizard.xml',
    'views/purchase_view.xml',
    'views/purchase_requisition_report.xml',
    'edi/purchase_requisition_action_data.xml',
    ],
}
