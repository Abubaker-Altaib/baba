# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Purchase Management Custom',
    'version': '2.0',
    'category': 'Purchase Management',
    'description': """Module for purchase Requisition management, It gives the purchase user the ablitiy to:
			* create purchase requesition.
			* insert the quotations for more than one supplier and product's prices.
			* Select one supplier and chose the reasons on which this supplier was selected.
			* Create purchase order from selected quotation. 
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['purchase_no_pricelist','base_vat','hr_custom'],
    'init_xml': [],
    'data': [
           'security/custom_purchase_security.xml',
           #'security/ir.model.access.csv',
           'purchase_view.xml',
           'internal_requesition_view.xml',
           'quote_view.xml',
           #'partner_view.xml',
           'custom_product_view.xml',
           'internal_requesition_workflow.xml',
           'quote_workflow.xml',
           'purchase_workflow.xml',
           #'sequence/internal_requesition_sequence.xml',
           #'sequence/quote_sequence.xml',
           'custom_purchase_reports.xml',
    ],
   'test': [
        'test/internal_requesition.yml',
        'test/quote.yml',
        'test/procurment.yml',
        'test/internal_requestion&quotereport.yml'
    ],
    
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
