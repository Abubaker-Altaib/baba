# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Purchase Transportations',
    'version': '1.0',
    "category": 'Generic Modules/Purchase Transportations',
    'description': """
    A Purchase transportations module is for generating transportations or carriers for purchase orders items from one location to another.
    A transportations order can be created form purchase order or from the form of the object.
    """,
    'author': 'NCTR',
    'website': 'www.nctr.sd',
    'depends': ['base', 'purchase','purchase_foreign','purchase_contracts','account_voucher'],
    'data': [
             'purchase_view.xml',
	     'transportation_report_view.xml',
             'company_view.xml',
             'transportation_order_sequence.xml',
             'transportation_order_view.xml',
	         #'workflow/transportation_workflow.xml',
             'workflow/transportation_quote_workflow.xml',
             'wizard/create_transportation_from_po.xml',
             'wizard/transporters_report.xml',
            ],
    'installable': True,
    'active': False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
