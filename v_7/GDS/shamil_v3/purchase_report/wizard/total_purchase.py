# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class total_purchase(osv.osv_memory):
    _name = "total.purchase"
    _description = "Total purchase"
    _columns = {
        'from_date': fields.date('Date From', required=True,), 
        'to_date': fields.date('Date To', required=True), 
        'product': fields.many2one('product.product', 'Product'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase_total.report',
            'datas': datas,
            }
total_purchase()
