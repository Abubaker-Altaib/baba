# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': ' Purchase Contracts',
    'version': '1.0',

    'description': """

Contracts 
=======================
    The specific and easy-to-use Contract system allows you to generate contracts with supplier or other types of contracts.
    A purchase order is created for the particular contract of purchase type.

    """,
    'author': 'NCTR',
    'website': 'www.nctr.sd',
    'depends': ['base_custom','purchase','purchase_custom','account_voucher_custom'],
    'data': [#'wizard/create_partial_purchase_order.xml',
             'view/contract_view.xml',
	         #'contract_report_view.xml',
                 #'wizard/programming_contracts.xml',
                 #'wizard/contracts_purchase_order.xml',
                 #'wizard/dept_state.xml',
                 #'wizard/payments_state.xml',
                 #'wizard/goods_details.xml',
                 #'wizard/payment_deptness.xml',

	         'view/purchase_view.xml',

                 #'contract_sequence.xml',
	         
#            'workflow/contract_workflow.xml',
#                 'workflow/contract_shipment_workflow.xml',
#                 'workflow/contract_fees_workflow.xml',

		         #'security/purchase_contract_group.xml',
             ],
    'installable': True,
    'active': True,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
