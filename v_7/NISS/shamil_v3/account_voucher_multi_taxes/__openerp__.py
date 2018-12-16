# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Voucher Multi Tax',
    'author': 'NCTR',
    'version': 'Shamil-1.0',
    'category': 'Generic Modules/Accounting',
    'description': """Module adding the multi-taxs.
    """,
    'website': 'http://www.nctr.sd',
    'depends': ['account_voucher_custom','account_check_writing_custom'],
    'data': [
        'voucher_multi_tax_view.xml',
        'voucher_sale_receipt_view.xml',
        'account_voucher_workflow.xml',
    ],
    'test': [],
    'demo_xml': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:







