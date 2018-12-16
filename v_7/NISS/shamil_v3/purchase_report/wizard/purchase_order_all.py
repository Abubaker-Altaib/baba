# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchase_order_all(osv.osv_memory):
    _name = "purchase.order.all"
    _description = "Purchase order all"
    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True), 
        'type' : fields.selection([('internal','Internal'),('foreign','Foreign')],'Type'),
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
            'report_name': 'Purchase_Order.report',
            'datas': datas,
            }

purchase_order_all()
