# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time
from datetime import datetime

class purchase_requisition_order_wiz(osv.osv_memory):
    """ To manage services reports """
    _name = "purchase.requisition.order.wiz"

    _description = "Purchase Requisition Order"

    _columns = {
        'date_from':fields.date('Date From', required=True,), 
        'date_to':fields.date('  Date To', required=True),
        'category_id':fields.many2one('product.category', 'Product Category'),
        'department_id':fields.many2one('hr.department', 'Department',),
        'partner_id':fields.many2one('res.partner', 'Supplier',),
    }


    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.requisition',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.requisition.order',
            'datas': datas,
            }

