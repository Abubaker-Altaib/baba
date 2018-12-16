# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


{
    'name': 'Foreign Purchase',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """Foreign Purchase
    """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': [
       'base', 'purchase', 'account_voucher','base_custom','purchase_custom','purchase_no_pricelist',
    ],
    'data': [
        'security/purchase_foreign_group.xml',
        'wizard/create_partial_purchase_order.xml',
        'internal_requesition_view.xml',
        'quote_view.xml',
        'purchase_view.xml',
        'letter_of_credit_sequense.xml',
        'purchase_letter_of_credit_view.xml',
        'company_view.xml',
        'workflow/letter_of_credit_workflow.xml',
        'purchase_foreign_reports_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
