# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchase_order_approved(osv.osv_memory):
    _name = "purchase.order.approved"
    _description = "Purchase order approved"

    STATE_SELECTION = [
        ('draft', 'مبدئي'),
        ('sign', 'توقيع مدير قسم المشتريات'),
        ('approved', 'تم تصديقه'),
        ('done', 'تم'),
        ('cancel', 'ملغي'),
        ('except_picking', 'استثناء الاستلام'),
        ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'state': fields.selection(STATE_SELECTION, 'State', help="The state of the contract.", select=True), 
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'Purchase_Order_approved.report',
            'datas': datas,
            }
purchase_order_approved()
    